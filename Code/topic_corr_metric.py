# -*- coding: utf-8 -*-
#!/usr/bin/python

import re
import sys
import csv
import time
import gensim
import sys
import numpy as np
import pandas as pd


'''
Function to put model results in dataframe where the index is the index of each word
and column is probability accross diff topics
'''
def fill_topic_matrix(corp_dictionary, model):
	results_df = pd.DataFrame(index = dictionary.keys(), columns = [i for i in xrange(0, model.num_topics) ] )
	# create temporary df for each topic with topic words and probabilities
	for i in xrange(0, model.num_topics):
		topic_probs = model.show_topic(i)

		temp = pd.DataFrame(topic_probs, columns = ['prob','token'])
		temp.index = temp.token.map(lambda x: corp_dictionary.token2id[x])

		for j in temp.index:
			results_df.ix[j][i] = temp.ix[j].prob

	results_df = results_df.fillna(0)
	return results_df


'''
To run: python topic_corr_metric.py <path2model><path2dionary>
'''
if __name__=="__main__":
	path2model = sys.argv[1]
	corpus_dict = sys.argv[2]
	# load model
	# path2Goodmodel   = 'LDA_alpha_0.05_eta_0.05_2015_1204_0309.model'
	model = gensim.models.LdaModel.load(path2model)
	# load dictionary
	# dictionary = gensim.corpora.Dictionary.load('SampleCorpus_Extreme_WithMm.dict')
	dictionary = gensim.corpora.Dictionary.load(corpus_dict)

	# get correlation of topics
	results_df = fill_topic_matrix(dictionary, model)
	topic_corr = results_df.corr()
	k = model.num_topics
	topic_score = (topic_corr.sum(axis=1).sum() - np.trace(topic_corr))/2
	topic_score = topic_score/k
	print "Topic score as a percentage of correlation based on the number of topics", "%.2f%%" % (100 * topic_score)
