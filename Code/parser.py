mport sys, os
from bs4 import BeautifulSoup as bs
import json
import xml.etree.ElementTree as ET
import gc

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


# For a single file
def ParseXML(filename):
    chunk=''
    with open(filename,'r') as f:
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
                        write_f=open(patent_id + '.xml', 'w')
                        print 'writing to ' + patent_id + '.xml  . . . . '
                        write_f.write(new_soup.prettify().encode('utf-8'))
                        write_f.close()
                    except:
                        pass
                soup.decompose()
                chunk=line
            else:
                chunk+=line
    print "File " + filename + " complete"

if __name__ == '__main__':
    print "*" * 45
    print "Begin processing."
    print "*" * 45
    reload(sys)
    sys.setdefaultencoding('UTF8')
    inpth = sys.argv[1]    
    os.chdir(inpth)
    fls = os.listdir(inpth)
    print fls
    fls = [f for f in fls if ".xml" in f]
    print fls
    for i in fls:
        print i
        ParseXML(i)
    print "*" * 45
    print "Processing complete."
    print "*" * 45


#-----------------------
# End
#-----------------------
