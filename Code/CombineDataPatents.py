# -*- coding: utf-8 -*-
"""
Created on Thu Nov  5 20:52:04 2015

@author: franciscojavierarceo
"""

import csv
csv.field_size_limit(sys.maxsize)
def Write(filename,myoutfile):
    with open(filename) as f:
        myreader = csv.reader(f,delimiter='|')
        for idx,line in enumerate(myreader):
            if (idx % 10000)==0:
                print "Iteration " + str(idx) + " complete."
            myoutfile.writerow(line)

f1 = '/Users/franciscojavierarceo/GitHub/patents/Code/2014/CSV/GS_ModelData.csv'
f2 = '/Users/franciscojavierarceo/GitHub/patents/Code/2013/CSV/GS_ModelData.csv'
f3 = '/Users/franciscojavierarceo/GitHub/patents/Code/2012/CSV/GS_ModelData.csv'
f4 = '/Users/franciscojavierarceo/GitHub/patents/Code/2011/CSV/GS_ModelData.csv'
f5 = '/Users/franciscojavierarceo/GitHub/patents/Code/2010/CSV/GS_ModelData.csv'

outfile = '/Users/franciscojavierarceo/GitHub/patents/Data/GS_ModelDataFull.csv'
csvfile = open(outfile, 'wb')
myoutfile = csv.writer(csvfile, delimiter='|')
files = [f1,f2,f3,f4,f5]
for i in files:
    Write(i,myoutfile)
    print "File " +i+ " Complete."

csvfile.close()


def file_len(fname):
    with open(fname) as f:
        myreader = csv.reader(f,delimiter='|')
        for idx,line in enumerate(myreader):
            pass
    return idx+1
    

#file_len(outfile)
file_len(f1) # 301,592
file_len(f2) # 278,559
file_len(f3) # 253,684
file_len(f4) # 4,635
file_len(f5) # 3,827
301592+278559+253684+4635+3827