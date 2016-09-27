# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 15:11:02 2015

@author: akhan

"""
import unicodecsv as csv

# Writes Vocabulary to File with (id,word,freq)
def write_vocabulary(corpus=None,outpth=None):
    outpth+='/vocab.csv'
    freq=corpus.dictionary.dfs
    words=(corpus.dictionary.items())
    sorted_words=sorted(words,key=lambda x: freq[x[0]],reverse=True)
    with open(outpth, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for item in sorted_words:
            writer.writerow([str(item[0]),item[1],str(freq[item[0]])])
    
def read_vocabulary(inpath,num_of_words=50):
    file_in=inpath
    li=[]
    with open(file_in, 'rb') as csvfile:
        myreader = csv.reader(csvfile, delimiter=",")
        for row in myreader:
          li.append((int(row[0]),row[1],int(row[2])))
    #li=map(lambda x: unicode(x[1]),li[0:num_of_words])
    return li[:num_of_words]

def prettify(vec,input_type=None):
    if input_type=="topic":
        return map(lambda x: str(x[1]),vec)
    if input_type=="document":
        return map(lambda x: round(x[1]*100,1),vec)
