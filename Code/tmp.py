from multiprocessing import Pool
from stemming.porter2 import stem
import gensim
import logging
import sys
import csv
import string
import time
from nltk.corpus import stopwords

# for printing logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
csv.field_size_limit(sys.maxsize)
stoplist = stopwords.words('english')
p = Pool(8)

class MyCorpus(object):
    def __init__(self, path2file):
        start_corpus = time.clock()
        self.path2file = path2file
        self.dictionary = gensim.corpora.Dictionary(self.getDocument(self.path2file,9))
        stop_ids = [self.dictionary.token2id[stopword] for stopword in stoplist if stopword in self.dictionary.token2id]
        sparse_ids= [tokenid for tokenid, docfreq in self.dictionary.dfs.iteritems() if docfreq <= 1]
        special_ids= [self.dictionary.token2id[wid] for wid in self.dictionary.token2id.keys() if wid.isdigit() and wid.isalnum()]
        self.dictionary.filter_tokens(stop_ids + sparse_ids + special_ids) # remove stop wrods, sparse terms, and numeric/special chars
        self.dictionary.compactify() # remove gaps in id sequence after words that were removed
        print "*" * 20 , "\nFinished LDA in:",str((time.clock() - start_corpus)),"secs\n", "*" * 20

    def getDocument(self,filename,col):
        with open(inpth) as f:
            myreader = csv.reader(f,delimiter="|")
            for c, doc in enumerate(myreader,1):
                yield self.processdoc(doc,col)

    def processdoc(self,doc,col):
        return doc[col].lower().translate(None,string.punctuation).split()

    def __iter__(self):
        for row in self.getDocument(self.path2file,9):
            yield self.dictionary.doc2bow(row)
            
class MyStemmedCorpus(MyCorpus):
    def processdoc(self,doc,col):
         return p.map(stem,doc[col].lower().translate(None,string.punctuation).split())


inpth = '/Users/franciscojavierarceo/GitHub/patents/Code/PatentData.csv'
inpth = '/Users/franciscojavierarceo/GitHub/patents/Code/LargePatentData.csv'
print "Running unstemmed corpus"
corpus1 = MyCorpus(inpth)
print "Running stemmed corpus"
corpus2 = MyStemmedCorpus(inpth)

#origwrds = list(corpus1.dictionary.token2id.keys())
#stemwrds= list(corpus2.dictionary.token2id.keys())

#print "Stemming made the corpus go from "+str(len(origwrds))+' to '+str(len(stemwrds))
#print "Stemming reduced the corpus by "+str(len(origwrds)-len(stemwrds))

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

file_len('/Users/franciscojavierarceo/GitHub/patents/Code/LargePatentData.csv')