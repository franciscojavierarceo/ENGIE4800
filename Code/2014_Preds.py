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
import numpy as np
import pandas as pd
from gensim import corpora
from multiprocessing import Pool
from stemming.porter2 import stem
from nltk.corpus import stopwords
import pyLDAvis.gensim as gensimvis
from sklearn.metrics.pairwise import cosine_similarity
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
csv.field_size_limit(sys.maxsize)       # Setting the maximum for csv limit
stoplist = stopwords.words('english')   # Pulling the stop words from gensim's list
p = Pool(8) # Specifying the number of cores I have on my computer

# For printing loggingldamod =gensim.models.LdaModel.load('/Users/franciscojavierarceo/GitHub/patents/Code/2014/out/DSGS_LDA2015_1019_2222.model')
def cleanup(x):
    # This handles "-/\" characters and replaces them with spaces instead of removing them
    # This also swaps out non-ascii characters for question marks and removes them
    for i in (string.punctuation[12]+string.punctuation[14]+string.punctuation[23]):
        x = x.replace(i,' ')
    return x.decode('utf-8').encode('ascii','ignore').translate(None,string.punctuation)

class ScoreCorpus(object):
    def __init__(self, path2file,ldamodel):
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
            c = 0
            myreader = csv.reader(f,delimiter="|")
            for doc in myreader:
                c+=1
                if c > 2:
                    break
                yield self.processdoc(doc,col)

    def processdoc(self,doc,col):
        return cleanup(doc[col].lower()).split()

    def __iter__(self):
        for row in self.getDocument(self.path2file,8):
            yield self.dictionary.doc2bow(row)
            

def getTermFreq(d):
    cdf = pd.DataFrame(d.token2id.keys(),columns=['Words'])
    cdf['TokenID'] = d.token2id.viewvalues()
    cdf = cdf.sort_values(by=['TokenID'],axis=0,ascending=True)
    cdf['Count']= d.dfs.values()
    cdf['WordLength'] = [len(i) for i in cdf['Words']]
    cdf = cdf.sort_values(by='Count',ascending=False)
    return cdf

def extract(x):
    return [item for sublist in x for item in sublist]

def returnTopicDF(x): 
    c = 0
    tpc_tpcs = []
    tpc_wrds = []
    tpc_prbs = []
    for tpc in x:
        c+=1
        wrds = []
        prbs = []    
        for i in tpc.split('+'):
            prbs.append(i.strip().split("*")[0])
            wrds.append(i.strip().split("*")[1])
        tpc_wrds.append(wrds)
        tpc_prbs.append(prbs)
        tpc_tpcs.append( ('Topic'+str(c),)*len(prbs))
    vdf = pd.DataFrame(extract(tpc_tpcs),columns=['Topic'])
    vdf['Words'] = extract(tpc_wrds)
    vdf['Probs'] = extract(tpc_prbs)
    return vdf

def fill_topic_matrix(corp_dictionary, model,nwords):
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

def ExportPredictions(corpus,fi,fo,ldamodel,topics):
    f = open(fi)
    fp = open(fo, 'wb')
    myreader = csv.reader(f,delimiter="|")
    mycsv = csv.writer(fp, delimiter='|')            
    docs = []
    predictedTopics=[]
    predictedTopicsDesc=[]
    rowout = []
    c = 0
    for row, document in itertools.izip(myreader,corpus):
        docs.append(document)
        docpreds = ldamodel[document]
        docpredsout =[]
        tmppreddoc = []
        tmprow = []
        for docpred in docpreds:
            tmppreddoc.append('Topic '+str(docpred[0]))
            docpredsout.append('+'.join(topics[docpred[0]].split('+')[0:9]).strip())
            tmprow.append(row[0:2])
        predictedTopicsDesc.append(docpredsout)
        predictedTopics.append(tmppreddoc)
        rowout.append(tmprow)
        odf = pd.DataFrame(tmprow,columns=['PatentID','PatentDate'])
        odf['Topic']=  tmppreddoc 
        odf['TopicSummary'] = docpredsout
        mycsv.writerows(odf.values.tolist())
        c+=1
        if ((c+1)%10000)==0:
            print c,'rows written to',fp
    return c

def topicCorrelation(results_df):
    topic_corr = results_df.corr()
    M = np.matrix(np.eye(topic_corr.shape[0], dtype=bool))
    maxval = np.sum(M==False)/2
    topic_score = ((topic_corr.sum(axis=1).sum() - np.trace(topic_corr))/2 ) / maxval
    print "Topic score as a percentage of correlation based on the number of topics", "%.2f%%" % (100 * topic_score)
    return topic_score

def topicCosineSimilarity(results_df):
    k = results_df.shape[1]
    cosineMatrix= np.zeros((k,k))
    for i in results_df.columns:
        for j in results_df.columns:
            cosineMatrix[i,j] = cosine_similarity(results_df[i],results_df[j])[0][0]
    M = np.matrix(np.eye(cosineMatrix.shape[0], dtype=bool))
    maxval = np.sum(M==False)/2
    topic_score = ((cosineMatrix.sum(axis=1).sum() - np.trace(cosineMatrix))/2 ) / maxval
    print "Topic score as a percentage of correlation based on the number of topics", "%.2f%%" % (100 * topic_score)    
    return topic_score

def EvaluateTopics(topics,cpcwords):
    fll = []
    for topic_i, cword_i in itertools.product(enumerate(topics),enumerate(cpcwords)):
        fll.append([topic_i[1],cword_i[0]])
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

def StemTopics(topics):
    stemmedTopics=[]
    for topic in topics:
        stemmedwords= []
        for word in topic:
            stemmedwords.append(stem(word))
        stemmedTopics.append(stemmedwords)
    return stemmedTopics

def TopicTermLength(topics):
    out = []
    for topic in topics:
        for word in topic:
            out.append(len(word))
    return out
        
# Specifying input paths and directories of relevant files
cpcpth = '/Users/franciscojavierarceo/GitHub/patents/Analysis/50sigterms_desc.pkl'
abscpcpth= '/Users/franciscojavierarceo/GitHub/patents/Analysis/abstract_mainclass_50sigterms_desc.pkl'
inpth = '/Users/franciscojavierarceo/GitHub/patents/Data/2014/2014_GS_ModelData.csv'
cpcwords = loadTop50SigWords(cpcpth)
abscpcwords = loadTop50SigWords(abscpcpth)
df1 = pd.read_csv('/Users/franciscojavierarceo/GitHub/patents/Data/2014/2014_GS_ModelData.csv',sep='|',nrows=5)
ldamod =gensim.models.LdaModel.load('/Users/franciscojavierarceo/GitHub/patents/Analysis/DSGS_LDA2015_1209_1725.model')
ldamod2 =gensim.models.LdaModel.load('/Users/franciscojavierarceo/GitHub/patents/Analysis/DSGS_LDA_last2015_1210_0124.model')
ldamod3 =gensim.models.LdaModel.load('/Users/franciscojavierarceo/Downloads/LDA_alpha_0.005_eta_0.005_2015_1211_1126.model')
corpus = corpora.MmCorpus('/Users/franciscojavierarceo/GitHub/patents/Analysis/Corpus/2014FullCorpus2.mm')
#dictionary = pickle.load('/Users/franciscojavierarceo/GitHub/patents/Analysis/Corpus/2014_FullCorpus2.dict')
dictionary = gensim.utils.SaveLoad.load('/Users/franciscojavierarceo/GitHub/patents/Analysis/Corpus/2014FullCorpus2.dict')
df1 = pd.read_csv('/Users/franciscojavierarceo/GitHub/patents/Data/2014/2014_GS_ModelData.csv',sep='|',nrows=5)
#Justin Law [4:30 PM] 
#topicname, topicterm, weight for each line
#for distribution on topics: patentid, topicname, weight
#topicname can be whatever, numbers are fine
topics = ldamod.show_topics(200,100)
cdf = getTermFreq(dictionary)
tdf = returnTopicDF(topics)
tdf.to_csv('/Users/franciscojavierarceo/GitHub/patents/Analysis/TopicDistributionsModel10passes.csv')
cdf = getTermFreq(dictionary)
f0 = '/Users/franciscojavierarceo/GitHub/patents/Data/2014/2014_GS_ModelData New.csv'
f1 ='/Users/franciscojavierarceo/GitHub/patents/Data/2014/2014_Predictions.csv'
ExportPredictions(corpus,f0,f1,ldamod,topics)   

# How to print the tokens for each document
#print [ cdf[cdf['TokenID']==i[0]].values for i in docs[1] ] 
# Importing pred
preds = pd.read_csv('/Users/franciscojavierarceo/GitHub/patents/Data/2014/2014_Predictions_20151212_1007.csv',sep='|',header=None)
preds.to_csv('/Users/franciscojavierarceo/GitHub/patents/Data/2014/2014_Predictions.csv',sep='|',index=False)
preds.columns = ['Patent_Id','Patent_Date','Predicted_Topic','Topic_Equation']
# Producing summaries
topics = ldamod.show_topics(200,100)
cdf = getTermFreq(dictionary)
tdf = returnTopicDF(topics)
cdf = getTermFreq(dictionary)
# Calculating shit
results_df = fill_topic_matrix(dictionary, ldamod)
results_df2 = fill_topic_matrix(dictionary, ldamod2)
results_df3 = fill_topic_matrix(dictionary, ldamod3)
model1score = topicCorrelation(results_df)
model2score = topicCorrelation(results_df2)
model3score = topicCorrelation(results_df3)
model1cosine= topicCosineSimilarity(results_df)
model2cosine= topicCosineSimilarity(results_df2)
model3cosine= topicCosineSimilarity(results_df3)
topics1 = getTopTopics(ldamod,200,50)
topics2 = getTopTopics(ldamod2,200,50)
topics3 = getTopTopics(ldamod3,200,50)
topics1stemmed = StemTopics(topics1)
topics2stemmed = StemTopics(topics2)
topics3stemmed = StemTopics(topics3)
# Term Length
len_tpc1 = np.mean(TopicTermLength(topics1))
len_tpc2 = np.mean(TopicTermLength(topics2))
len_tpc3 = np.mean(TopicTermLength(topics3))

# Performance of model 1
cpc_edf, cpc_acc = EvaluateTopics(topics1,cpcwords)
abs_edf, abs_acc = EvaluateTopics(topics1,abscpcwords)
cpc_edfs, cpc_accs = EvaluateTopics(topics1stemmed,cpcwords)
abs_edfs, abs_accs = EvaluateTopics(topics1stemmed ,abscpcwords)
# Performance of model 2
cpc_edf2, cpc_acc2 = EvaluateTopics(topics2,cpcwords)
abs_edf2, abs_acc2 = EvaluateTopics(topics2,abscpcwords)
cpc_edf2s, cpc_acc2s = EvaluateTopics(topics2stemmed,cpcwords)
abs_edf2s, abs_acc2s = EvaluateTopics(topics2stemmed,abscpcwords)
# Performance of model 3
cpc_edf3, cpc_acc3 = EvaluateTopics(topics3,cpcwords)
abs_edf3, abs_acc3 = EvaluateTopics(topics3,abscpcwords)
cpc_edf3s, cpc_acc3s = EvaluateTopics(topics3stemmed,cpcwords)
abs_edf3s, abs_acc3s = EvaluateTopics(topics3stemmed,abscpcwords)

kl_div1 = 0
kl_div2 = 0
kl_div3 = 0
print '*'*90
print 'Model 1 has a topic correlation of',model1score*100
print '\t a cosine similarity of',model1cosine*100
print '\t a KL-divergence of',kl_div1
print '\t a CPC similarity of',cpc_acc*100
print '\t a Abstract similarity of',abs_acc*100
print '\t a stemmed-CPC similarity of',cpc_accs*100
print '\t a stemmed-Abstract similarity of',abs_accs*100
print '\t an average word length of',len_tpc1

print '*'*90
print 'Model 2 has a topic correlation of',model2score*100
print '\t a cosine similarity of',model2cosine*100
print '\t a KL-divergence of',kl_div2
print '\t a CPC similarity of',cpc_acc2*100
print '\t a Abstract similarity of',abs_acc2*100
print '\t a stemmed-CPC similarity of',cpc_acc2s*100
print '\t a stemmed-Abstract similarity of',abs_acc2s*100
print '\t an average word length of',len_tpc2
print '*'*90
print 'Model 3 has a topic correlation of',model3score*100
print '\t a cosine similarity of',model3cosine*100
print '\t a KL-divergence of',kl_div3
print '\t a CPC similarity of',cpc_acc3*100
print '\t a Abstract similarity of',abs_acc3*100
print '\t a stemmed-CPC similarity of',cpc_acc3s*100
print '\t a stemmed-Abstract similarity of',abs_acc3s*100
print '\t an average word length of',len_tpc3
print '*'*90

f = open('/Users/franciscojavierarceo/GitHub/patents/Data/2014/2014_GS_ModelData New.csv')
myreader = csv.reader(f,delimiter="|")
patent = []
c = 0
for row in myreader:
    c+=1
    if row[0]=='08817437':
        patent = [row]
        print 'Found patent 08817437 in row',c
        break

