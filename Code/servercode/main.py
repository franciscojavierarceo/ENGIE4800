# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 18:36:36 2015

@author: akhan
"""

# fix quotation marks issue
import os
os.chdir('/home/akhan/Work/lda_server')

from ldaModel_server_multi import *
import helper
path_vocab   = '/home/akhan/Work/lda_server/output/vocab.csv'
path_maincsv = '/home/akhan/Work/csv_data/GS_ModelData.csv'
path_output  = '/home/akhan/Work/lda_server/output/'

corpus=createCorpus(inpth=path_maincsv,outpth=path_output,stemcorpus=False,stoplist=[])
helper.write_vocabulary(corpus,path_output)
freq_words=helper.read_vocabulary(path_vocab,50)
freq_words=[x[1] for x in freq_words]
corpus.removeWords(freq_words)

model=runLDA(k=20,corpus=corpus,outpth=path_output,alpha='symmetric',eta=None,num_of_cores=1,num_of_passes=1,chunk_size=5000)
