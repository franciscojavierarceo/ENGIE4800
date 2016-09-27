# -*- coding: utf-8 -*-
"""
Created on Tue Dec  8 21:25:16 2015

@author: franciscojavierarceo
"""
# -*- coding: utf-8 -*-
"""
Created on Mon Dec  7 23:24:06 2015

@author: franciscojavierarceo
"""

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
        sparse_ids= [tokenid for tokenid, docfreq in self.dictionary.dfs.iteritems() if docfreq <= 10]
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

            
inpth = '/Users/franciscojavierarceo/GitHub/patents/Code/2014/CSV/GS_ModelData.csv'
outpth = '/Users/franciscojavierarceo/GitHub/patents/Analysis/'
corpus = MyCorpus(inpth)
corpora.MmCorpus.serialize(outpth+'Corpus/2014FullCorpus2.mm', corpus)
corpus.dictionary.save(outpth+'Corpus/2014FullCorpus2.dict')
k = 200
lda = gensim.models.ldamodel.LdaModel(corpus = corpus, id2word = corpus.dictionary, num_topics = k, update_every = 20000, chunksize = 40000, passes=10)
lda.save(outpth+'DSGS_LDA'+time.strftime('%Y_%m%d_%H%M',time.localtime())+'.model')
lda2 = gensim.models.ldamodel.LdaModel(corpus = corpus, id2word = corpus.dictionary, num_topics = k, update_every = 1, chunksize = 5000, passes=1,iterations=50)
lda2.save(outpth+'DSGS_LDA_last'+time.strftime('%Y_%m%d_%H%M',time.localtime())+'.model')
# Building visualization
vis_corpus = corpora.MmCorpus(outpth+'Corpus/2014FullCorpus2.mm')
vis_data = gensimvis.prepare(lda2, vis_corpus, corpus.dictionary)
pyLDAvis.save_html(vis_data,outpth+'LDA_Model_Visualization_Model.html')
vis_data0 = gensimvis.prepare(lda, vis_corpus, corpus.dictionary)
pyLDAvis.save_html(vis_data0,outpth+'LDA_Model_Visualization_ModelOriginal.html')


