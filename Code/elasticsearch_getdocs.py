import elasticsearch
import time

es = elasticsearch.Elasticsearch('http://elasticsearch-cloud.cloudapp.net:9200/')

# comment out specific fields both in the query and the request loop below for faster extraction
query={"fields" : ["us-patent-grant.us-bibliographic-data-grant.invention-title.#text",
                   "us-patent-grant.us-bibliographic-data-grant.publication-reference.document-id.doc-number",
                   "us-patent-grant.description", 
                   "us-patent-grant.abstract", 
                   "us-patent-grant.claims.claim"], 
       "query" : {"match_all" : {}}}

#scroll indicates time the search request is open, 10m = 10 mins, size is the number of records retrieved each response
#10m is sufficient for ~5000 docs, increase scroll time for more recrods 
scanResp= es.search(index="patents", doc_type="patent", body=query, search_type="scan", scroll="10m", size=500)  
scrollId= scanResp['_scroll_id']
scroll_size = scanResp['hits']['total']

ids = set()
titles = {}
abstracts = {}
claims = {}
descriptions = {}

start_time = time.time()

while scroll_size > 0:
    print len(ids)
    print "Scrolling..."
    response= es.scroll(scroll_id=scrollId, scroll= "10m")
    for hit in response['hits']['hits']:
        docid = hit['fields']['us-patent-grant.us-bibliographic-data-grant.publication-reference.document-id.doc-number'][0]
        ids.add(docid)
        try:
            titles = hit['fields']['us-patent-grant.us-bibliographic-data-grant.invention-title.#text'][0]
        except KeyError:
            pass
        try:
            # may be multiple claims, so instead of text this will be an array
            claims[docid] = hit['fields']['us-patent-grant.claims.claim']
        except KeyError:
            pass          
        try:
            abstracts[docid] = hit['fields']['us-patent-grant.abstract'][0]
        except KeyError:
            pass
        try:
            descriptions[docid] = hit['fields']['us-patent-grant.description'][0]
        except KeyError:
            pass
    scrollId = response['_scroll_id']
    scroll_size = len(response['hits']['hits'])
    if len(ids) >= 5000: #stop when more than 5000 docs have been retrieved
        break

print("--- %s seconds ---" % (time.time() - start_time))