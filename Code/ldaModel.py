# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Updated: Thu Oct 29 22:03:29 2015

Authors: Gabi, Abdus, and Francisco
"""
import re
import sys
import csv
import time
import gensim
import pickle
import string
import logging
import pyLDAvis
import itertools
import pandas as pd
from gensim import corpora
from multiprocessing import Pool
from stemming.porter2 import stem
from nltk.corpus import stopwords
import pyLDAvis.gensim as gensimvis

# For printing logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
csv.field_size_limit(sys.maxsize)       # Setting the maximum for csv limit
stoplist = stopwords.words('english')   # Pulling the stop words from gensim's list
p = Pool(8) # Specifying the number of cores I have on my computer

'''
Class for Corpus streaming - one document at a time in memory
	* Loop through each document in Description column, tokenize, filter out stop words & punctuation, lower
        	  keep only alpha numeric words
	* Create dictionary mapping which assigns a unique integer id to all words appearing in corpus
	* loop through the list of lists of words and convert tokenized documents to vectors
	* doc2bow() counts the # of occurences of each distinct word, converts the word to its integer word id and
      	  returns the result as a sparse vector.
	* filter out stop words, special characters, and infrequent terms
	* the 8 here represents the 8th column of the csv file that is pipe-delimited (i.e.,"|")
	* the MyStemmedCorpus class is a modification of MyCorpus that 
         1. stems the words in description
         2. parallelizes the stemming
'''
def cleanup(x):
    # This handles "-/\" characters and replaces them with spaces instead of removing them
    # This also swaps out non-ascii characters for question marks and removes them
    for i in (string.punctuation[12]+string.punctuation[14]+string.punctuation[23]):
        x = x.replace(i,' ')
    return x.decode('utf-8').encode('ascii','ignore').translate(None,string.punctuation)

class MyCorpus(object):
    def __init__(self, path2file):
        self.path2file = path2file
        self.dictionary = gensim.corpora.Dictionary(self.getDocument(self.path2file,8))
        stop_ids = [self.dictionary.token2id[stopword] for stopword in stoplist if stopword in self.dictionary.token2id]
        sparse_ids= [tokenid for tokenid, docfreq in self.dictionary.dfs.iteritems() if docfreq <= 0]
        special_ids= [self.dictionary.token2id[wid] for wid in self.dictionary.token2id.keys() if wid.isdigit() and wid.isalnum()]
        shrtlng_ids = [self.dictionary.token2id[wordid] for wordid in self.dictionary.token2id if len(wordid) < 4 or len(wordid) > 50]
        numwrds_ids = [self.dictionary.token2id[wordid] for wordid in self.dictionary.token2id if re.search('[0-9]',wordid) is not None]
        # remove stop wrods, sparse terms, numeric/special chars, words with a short length, and words with numbers
        self.dictionary.filter_tokens(stop_ids + sparse_ids + special_ids + shrtlng_ids + numwrds_ids) 
        self.dictionary.compactify() # remove gaps in id sequence after words that were removed

    def getDocument(self,filename,col):
        with open(inpth) as f:
            myreader = csv.reader(f,delimiter="|")
            for doc in myreader:
                yield self.processdoc(doc,col)

    def processdoc(self,doc,col):
        return cleanup(doc[col].lower()).split()

    def __iter__(self):
        for row in self.getDocument(self.path2file,8):
            yield self.dictionary.doc2bow(row)
            
class MyStemmedCorpus(MyCorpus):
    def processdoc(self,doc,col):
         return p.map(stem,doc[col].lower().translate(None,string.punctuation).split())

def loadTop50SigWords(cpcwrdsfile):
    '''
    This loads the 50 most significant terms from Justin's original file
    '''
    pklfile = open(cpcwrdsfile,'rb')
    return pickle.load(pklfile)

def getTopTopics(ldamodel,k,j):
    '''
    This pulls the most probable words per topics
    '''
    topics = []
    for i in xrange(k):
        topics.append([i[1] for i in ldamodel.show_topic(i,j)])
    return topics
    
def EvaluateTopics(topics,cpcwords):
    fll = []
    for topic_i, cword_i in itertools.product(enumerate(topics),enumerate(cpcwords)):
        fll.append([topic_i[0],cword_i[0]])
    EvalDF = pd.DataFrame(fll)
    EvalDF.columns = ['TopicIndex','CPCIndex']
    ncorrect, nwords = [], []
    for cw in cpcwords:        
        for topic in topics:
            ncorrect.append(float(len([ i for i in cw if i in topic] ))) 
            nwords.append(float(len(cw)))
    EvalDF['Correct'] = ncorrect
    EvalDF['CPCWords'] = nwords
    totalacc = EvalDF['Correct'].sum(axis=0) /EvalDF['CPCWords'].sum(axis=0)
    print "The accuracy is =", totalacc
    return EvalDF,totalacc

def TopicQuality(ptopics):
    perf = []
    for topic in ptopics:
        perf.append(float(sum([len(word) for word in ptopics])) / len(topic))
    return perf

def runLDA(inpth,cpcwrdsfile,k,outpth,stemcorpus):
	'''
	Function does the following:
         * build dictionary mapping for words based on input file
         * build corpus as sparse vector
         * Run LDA online - use k topics with a chunksize of 1,000 documents
	'''
	print "*" * 20, "\nTokenizing and Building Corpus\n", "*" * 20
	start_corpus = time.clock()
	# create streaming corpus - doesnt load corpus into memory 
	if stemcorpus == False:
         corpus = MyCorpus(inpth)
         corpora.MmCorpus.serialize(outpth+'Corpus/FullCorpus.mm', corpus)
         corpus.dictionary.save(outpth+'Corpus/FullCorpus.dict')

	if stemcorpus == True:
         corpus = MyStemmedCorpus(inpth)    
         corpora.MmCorpus.serialize(outpth+'Corpus/StemmedCorpus.mm', corpus)
         corpus.dictionary.save('Corpus/StemmedCorpus.dict')
         	
	print "*" * 20 , "\nFinished Building Corpus in:",str((time.clock() - start_corpus)),"secs\n", "*" * 20
	dfc = pd.DataFrame(corpus.dictionary.token2id.keys(),columns=['Word'])
	dfc['IndexValue'] = corpus.dictionary.token2id.viewvalues()
	dfc['Count']= corpus.dictionary.dfs.values()
	dfc['WordLength'] = [len(i) for i in dfc['Word']] 
	dfc.to_csv(outpth+'Corpus/TermFrequencies.csv',sep=',',index=None) 
	cpcwords = loadTop50SigWords(cpcpth)
	abscpcwords = loadTop50SigWords(abscpcpth)
	start_lda = time.clock()
	print "*" * 20 , "\nBeginning LDA...","secs\n", "*" * 20
	lda = gensim.models.ldamodel.LdaModel(corpus = corpus, id2word = corpus.dictionary, num_topics = k, update_every = 20000, chunksize = 40000, passes=2)
	print "*" * 20 , "\nFinished LDA in:",str((time.clock() - start_lda)),"secs\n", "*" * 20
# 	This is the multicore version that is supposed to be fast...no luck with it yet.
# 	lda = gensim.models.ldamulticore.LdaMulticore(corpus = corpus, id2word = corpus.dictionary, num_topics = k,workers=3)
	lda.save(outpth+'DSGS_LDA'+time.strftime('%Y_%m%d_%H%M',time.localtime())+'.model')
	print "*" * 20 , "\nModel saved to:",outpth,"\n", "*" * 20
	print "Retreiving the topics..." 
	topics = getTopTopics(lda,k,50)
	edf, acc = EvaluateTopics(topics,cpcwords)
	edf2, acc2 = EvaluateTopics(topics,abscpcwords)
 	vis_corpus = corpora.MmCorpus(outpth+'FullCorpus.mm')
    	vis_data = gensimvis.prepare(lda, vis_corpus, corpus.dictionary)
    	pyLDAvis.save_html(vis_data,outpth+'LDA_Model_Visualization.html')
	print "The model accuracy based on the USPC classification is =", acc
	print "The model accuracy based on the Main classification is =", acc2

if __name__ == '__main__':
	print "*" * 45
	print "Begin processing."
	print "*" * 45
	reload(sys)
	sys.setdefaultencoding('UTF8')
#	To execute in the command line, use the two lines below and comment out the inpth and outpth
#	inpth = sys.argv[1] ; outpth = sys.arv[2]
	cpcpth = '/Users/franciscojavierarceo/GitHub/patents/Analysis/50sigterms_desc.pkl'
	abscpcpth= '/Users/franciscojavierarceo/GitHub/patents/Analysis/abstract_mainclass_50sigterms_desc.pkl'
#	inpth = '/Users/franciscojavierarceo/GitHub/patents/Code/test/GS_ModelData2.csv'
	inpth = '/Users/franciscojavierarceo/GitHub/patents/Data/GS_ModelDataFull.csv'
	outpth = '/Users/franciscojavierarceo/GitHub/patents/Analysis/'
	runLDA(inpth,cpcpth ,20,outpth,False)
# To this code cd into folder where this file is saved then, in ther terminal execute:
# > python ldaModel.py 'pathtofile/GS_Model.csv' /outputpath/
