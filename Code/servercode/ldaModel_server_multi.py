# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Updated: Thu Oct 29 22:03:29 2015

Authors: Gabi, Abdus, and Francisco
"""
'''
With 40 topics and 8870 patents, 1 passes, chunk=5000
Multicore version took: 682.852968 secs
With 40 topics and 8870 patents, 1 passes, chunk=5000
Singlecore version took: 819.06272 secs
'''

import gensim
import logging
import sys
import csv
import time
import string
from nltk.corpus import stopwords
from multiprocessing import Pool
from stemming.porter2 import stem
#import helper as hp

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
csv.field_size_limit(sys.maxsize)
p = Pool(3)

'''
Class for Streaming Corpus - Allows one document to be stored in memory at a time
	* Loop through each document in Description column, tokenize, filter out stop words & punctuation, lower
        	  keep only alpha numeric words
	* Create dictionary mapping which assigns a unique integer id to all words appearing in corpus
	* loop through the list of lists of words and convert tokenized documents to vectors
	* doc2bow() counts the # of occurences of each distinct word, converts the word to its integer word id and
  	  returns the result as a sparse vector.
	* filter out stop words, special characters, and infrequent terms
'''

class StreamingCorpus(object):
    def __init__(self, path2file,stoplist=[]):
        ss=10
        self.path2file = path2file
        self.dictionary = gensim.corpora.Dictionary(self.getDocument(self.path2file,9))
        self.dictionary.id2token = {v: k for k, v in self.dictionary.token2id.items()}
        print "Inital Vocabulary size :",len(self.dictionary.keys())
        stop_ids = [self.dictionary.token2id[stopword] for stopword in stoplist if stopword in self.dictionary.token2id]
        print "Removing %s out of %s words passed to corpus."%(len(stop_ids),len(stoplist))                        
        print "Sample:",map(lambda x:self.dictionary.id2token[x] ,stop_ids[:ss])
        sparse_ids= [tokenid for tokenid, docfreq in self.dictionary.dfs.iteritems() if docfreq <= 1]
        print "Removing %s words which occur only in one document"%(len(sparse_ids))  
        print "Sample:",map(lambda x:self.dictionary.id2token[x] ,sparse_ids[:ss])
        #xyz=map(lambda x: inv_map[x],sparse_ids)
        #import pdb
        #pdb.set_trace()
        numeric_ids= [self.dictionary.token2id[wid] for wid in self.dictionary.token2id.keys() if wid.isdigit()]
        print "Removing %s words which are numeric "%(len(numeric_ids))
        print "Sample:",map(lambda x:self.dictionary.id2token[x] ,numeric_ids[:ss])
        small_ids= [self.dictionary.token2id[wid] for wid in self.dictionary.token2id.keys() if len(wid) <=2]
        print "Removing %s words which have len <=2"%(len(small_ids))
        print "Sample:",map(lambda x:self.dictionary.id2token[x] ,small_ids[:ss])
        #self.dictionary.filter_tokens(stop_ids + sparse_ids + numeric_ids + small_ids) # remove stop wrods, sparse terms, and numeric/special chars
        print "Vocabulary size :",len(self.dictionary.keys())
        self.dictionary.compactify() # remove gaps in id sequence after words that were removed

    def removeWords(self,stoplist=[]):
        ids=[self.dictionary.token2id[stopword] for stopword in stoplist if stopword in self.dictionary.token2id]
        print "Removing %s out of %s words."%(len(ids),len(stoplist))                        
        self.dictionary.filter_tokens(ids) 
        print "Vocabulary size :",len(self.dictionary.keys())
        self.dictionary.compactify() # remove gaps in id sequence after words that were removed
        
    def getDocument(self,filename,col):
        with open(self.path2file) as f:
            myreader = csv.reader(f,delimiter="|")
            for doc in myreader:
                yield self.processdoc(doc,col)

    def processdoc(self,doc,col):
        return doc[col].lower().translate(None,string.punctuation).split()

    def __iter__(self):
        for row in self.getDocument(self.path2file,9):
            yield self.dictionary.doc2bow(row)
    def vocabularySize(self):
        return len(self.dictionary.keys())

class StemmedCorpus(StreamingCorpus):
    def processdoc(self,doc,col):
         return p.map(stem,doc[col].lower().translate(None,string.punctuation).split())

'''
Function does the following:
	* build dictionary mapping for words based on input file
	* build corpus as sparse vector
	* Run LDA online - use k topics with a chunksize of 1,000 documents
'''
def createCorpus(inpth,outpth=None,stemcorpus=True,stoplist=[]):
    print "*" * 20, "\nTokenizing and Building Corpus\n", "*" * 20
    start_corpus = time.clock()
    print "Stem Corpus set to           : %s"%(stemcorpus)
    print "Stopwords passed by user     : %s words"%(len(stoplist))
    nltk_stopwords=stopwords.words('english')
    print "Imported stopwords from NLTK : %s words"%(len(nltk_stopwords))
    stoplist = stoplist + nltk_stopwords    
    # create streaming corpus - doesnt load corpus into memory 
    if stemcorpus == True:
        corpus = StemmedCorpus(inpth,stoplist=stoplist)    
    else:
        corpus = StreamingCorpus(inpth,stoplist=stoplist)
    if outpth!=None:
        corpus.dictionary.save(outpth+'Corpus.dict')
        print "*" * 20 , "\nDictionary written to:",outpth,"\n", "*" * 20
    print "*" * 20 , "\nFinished Building Corpus in:",str((time.clock() - start_corpus)),"secs\n", "*" * 20
    return corpus

def runLDA(k,corpus,outpth=None,alpha='symmetric',eta=None,num_of_cores=1,num_of_passes=1,chunk_size=5000):
    print "*" * 20, "\nRunning LDA\n", "*" * 20
    start_lda = time.clock()
    if num_of_cores==1 or num_of_cores==None:
        print "Running Single-core LDA implementation"
        lda = gensim.models.ldamodel.LdaModel(corpus = corpus, id2word = corpus.dictionary, num_topics = k, update_every = 1, chunksize = chunk_size, passes=num_of_passes,alpha=alpha,eta=eta)
    else:
        print "Running Multi-core LDA implementation on %s cores" % (num_of_cores)
        lda = gensim.models.ldamulticore.LdaMulticore(corpus = corpus, id2word = corpus.dictionary, num_topics = k, chunksize = chunk_size, passes=num_of_passes,alpha=alpha,eta=eta,workers=num_of_cores)
    print "*" * 20 , "\nFinished LDA in:",str((time.clock() - start_lda)),"secs\n", "*" * 20
    print "Number of Passes : %s"%(num_of_passes)
    print "Chunk Size       : %s"%(chunk_size)
    print "alpha(symmetric) : %s"%(lda.alpha[0])
    print "eta              : %s"%(lda.eta)
    file_name="LDA_alpha_"+str(lda.alpha[0])+"_eta_"+str(lda.eta)+"_"+time.strftime('%Y_%m%d_%H%M',time.localtime())+'.model'    
    if outpth!=None:
        lda.save(outpth+file_name)
        print "*" * 20 , "\nModel written to:",file_name,"\n", "*" * 20
    print "*" * 20 , "\nFinished LDA in:",str((time.clock() - start_lda)),"secs\n", "*" * 20
    return lda


'''
if __name__ == '__main__':
    # for printing logging
    # Stop Words
    frequent_words=hp.read_vocabulary('/home/akhan/Documents/Capstone/LDAfiles/')
    my_stopwords=map(lambda x: unicode(x[1]),frequent_words[0:50])
 
    print "*" * 45
    print "Begin processing."
    print "*" * 45
    reload(sys)
    sys.setdefaultencoding('UTF8')
    inpth = '/home/akhan/Documents/Capstone/LDAfiles/GS_ModelData.csv'
    outpth = '/home/akhan/Documents/Capstone/LDAfiles/'
    corpus=createCorpus(inpth,outpth,stopwords=stoplist)
    #model=runLDA(k=20,corpus=corpus,outpth,alpha='symmetric',eta=None,num_of_cores=1)
    #(k,corpus,outpth=None,alpha='symmetric',eta=None,num_of_cores=1):
'''
