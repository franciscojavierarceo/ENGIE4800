import elasticsearch
import time
es = elasticsearch.Elasticsearch('http://elasticsearch-cloud.cloudapp.net:9200/')

## rertrieve uspc and doc counts

doc_count_limit = 100 # filter uspc classes that only have documents above this limit, use this to increase or reduce number of classes filtered

num_terms = 10 # number of significant terms retrieved, 10 is a good enough number as most classes don't even return 10 significant terms
uspc = {} # dictionary where key is the class and value is the number of documents associated with the class
significant_terms = {} # dictionary where key is the class and the value is a list of terms most significant terms in descending order
termdata = {} # dictionary where key is the class and the value are details of the term such as background count, foreground_count


# perform first query to find out all unique classes and count number of docs associated with each class
query = {
  "size": 0,
  "aggs": {
    "uspc": {
      "terms": { 
        "field" :"us-patent-grant.us-bibliographic-data-grant.classification-national.main-classification",
      "size": 0
      }
    }
  }
}

rs = es.search(index ="patents", doc_type="patent", body=query)

for hit in rs['aggregations']['uspc']['buckets']:
    uspc[hit['key']] = hit['doc_count']

# subset the classes based on the number of documents available
# this is done because if a class has only a few documents, significant terms is not meaningful
subset_classes = [x[0] for x in uspc.items() if x[1]>doc_count_limit]
print("%d of classes selected from %d of total classes." % (len(subset_classes), len(uspc)))

for item in subset_classes:
    query = {
      "size": 0,
      "query": {
        "filtered": {
          "filter": {
            "term": {
              "us-patent-grant.us-bibliographic-data-grant.classification-national.main-classification": item
            }
          }
        }
      },
      "aggs": {
        "most_popular": {
          "significant_terms": {
            "field": "us-patent-grant.abstract", 
            "size": num_terms
          }
        }
      }
    }
    rs = es.search(index ="patents", doc_type="patent", body=query)
    significant_terms[item] = [x['key'] for x in rs['aggregations']['most_popular']['buckets']]
    termdata[item] = rs['aggregations']['most_popular']['buckets']


## example of how to use the results
## following will return the top ten significant terms for a class
## results returned may be less than ten terms or even zero
print significant_terms[subset_classes[1]]



# uncomment this part if you want the pure count of terms rather than significant terms for each class
#for item in subset_classes:
#    query = {
#      "size": 0,
#      "query": {
#        "filtered": {
#          "filter": {
#            "term": {
#              "us-patent-grant.us-bibliographic-data-grant.classification-national.main-classification": item
#            }
#          }
#        }
#      },
#      "aggs": {
#        "most_popular": {
#          "terms": {
#            "field": "us-patent-grant.abstract", 
#            "size": num_terms
#          }
#        }
#      }
#    }
#    rs = es.search(index ="patents", doc_type="patent", body=query)
#    significant_terms[item] = [x['key'] for x in rs['aggregations']['most_popular']['buckets']]
