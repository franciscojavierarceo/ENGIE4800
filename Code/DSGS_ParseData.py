# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 17:45:36 2015

@author: franciscojavierarceo
"""
import itertools
from multiprocessing import Pool
import os, csv, sys, gc
from bs4 import BeautifulSoup as bs
def CheckUtility(soup):
    try:
        return soup.find('application-reference')['appl-type']=='utility'
    except:
        print 'No application reference was identified in this document'
def get_description(soup):
    try:
        return soup.find('description').get_text()
    except:
        pass
def get_abstract(soup):
    try:
        return soup.find('abstract').get_text()
    except:
        pass

def soup_change(soup):
    try:
        # Modify Description Tag
        desc_text=get_description(soup)
        soup.find('description').clear()
        soup.find('description').append(desc_text)
    except:
        pass
        # Modify Abstract Tag
    try:
        abs_text=get_abstract(soup)
        soup.find('abstract').clear()
        soup.find('abstract').append(abs_text)
    except:
        pass
    try:
        # Clear Drawings tag
        soup.find('drawings').clear()
    except:
        pass
    for i in soup.find_all('claim'):
        # Modify Claim-text 
        claim_text=i.get_text()
        i.clear()
        i.append(claim_text)
    return soup.find('publication-reference').find('doc-number').get_text(), soup

def ExportData(soup,patentid,wfile):
    # Want these fields as well
    # This gives the patent number    
    out = [patentid]
    varlist = ['date','orgname','invention-title',
               'department','number-of-claims','application-reference',
               'abstract','description']
    for i in varlist:
        if i =='application-reference':
            try:
                tmp = soup.find(i)['appl-type']
            except:
                tmp = ''
        else:
            try:
                tmp = soup.find(i).get_text()
            except:
                tmp = ''
        out.append(tmp)
    out = map(lambda out: out.strip(), out)             # Cleaned
    wfile.writerow(out)


def ParseXML(filenames,inpth,opth):
    chunk = ''
    varlist = ['PatentID','PatentDate','OrgName','Title',
           'Department','NClaims','ApplicationRef','Abstract','Description']
    fp = open(opth+'GS_ModelData.csv', 'w')
    for filename in filenames:
        with open(inpth+filename,'r') as f:
            mycsv = csv.writer(fp, delimiter='|')            
            mycsv.writerow(varlist)
            for line in f:
                x=line.strip()
                if x=='<?xml version="1.0" encoding="UTF-8"?>':
                    if chunk=='':
                        # skip the first part
                        continue
                    # Put it in beautifulsoup
                    gc.collect()
                    soup=bs(chunk) 
                    # Check if it is utility
                    if CheckUtility(soup):
                        try:
                            patent_id, new_soup=soup_change(soup)
                            # Pulling in the relevant fields
                            ExportData(new_soup,patent_id,mycsv)
                            # Exporting new small file
                            print 'writing to ' + patent_id + '.xml  . . . . '
                        except:
                            pass
                    soup.decompose()
                    chunk=line
                else:   
                    chunk+=line
        fp.close()
    
def ParallelParse(myargs):
    """Convert `f([1,2])` to `f(1,2)` call."""
    print myargs
    return ParseXML(*myargs)


if __name__ == '__main__':
    print "*" * 45
    print "Begin processing."
    print "*" * 45
    reload(sys)
    sys.setdefaultencoding('UTF8')
    inpth = sys.argv[1]
    outpth = sys.argv[2]
    fls = [f for f in os.listdir(inpth) if ".xml" in f]
    if os.path.exists(outpth)==False:
        os.mkdir(outpth)
    # This is the main function
    print "Input path = " + inpth
    print "Output path = " + outpth
    print "Filenames = " , fls    
#    inpth  = '/Users/franciscojavierarceo/GitHub/patents/Code/testparl/Original/'
#    outpth = '/Users/franciscojavierarceo/GitHub/patents/Code/testparl/CSV/'
# This is the parallelized version, but it fails to work
#    pool = Pool()
#    pool.map(ParallelParse, itertools.izip(fls, itertools.repeat(inpth),itertools.repeat(outpth)))
    # This currently is the only working version
    ParseXML(fls,inpth,outpth)
    print "*" * 45
    print "Processing complete."
    print "Data stored in " + outpth
    print "*" * 45
#-----------------------
# End
#-----------------------