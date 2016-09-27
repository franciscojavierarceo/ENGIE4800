## sample on how to retrieve data from elasticsearch

import elasticsearch
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

es = elasticsearch.Elasticsearch('http://elasticsearch-cloud.cloudapp.net:9200/')

fieldlist = ["us-patent-grant.us-bibliographic-data-grant.invention-title.#text.length", "us-patent-grant.abstract.length", "us-patent-grant.description.length", "us-patent-grant.claims.claim.length"]
fieldnames = ["title", "abstract", "description", "claim"]

lengths = {}

length_query = {
      "size": 0,
      "aggs": {
        "length": {
          "terms": { 
            "field" : 'us-patent-grant.abstract',
          "size": 0
          }
        }
      }
    }

missing_query = {
        "query": {
            "filtered": {
                "filter" :{
                    "missing": {
                        "field" : "us-patent-grant.abstract"
                    }
                }
            }
        }
    }

for i in range(len(fieldlist)):
    lengths[fieldnames[i]] = {}
    length_query['aggs']['length']['terms']['field'] = fieldlist[i]
    missing_query['query']['filtered']['filter']['missing']['field'] = fieldlist[i]
    rs = es.search(index ="patents", doc_type="patent", body=length_query, timeout="20m")
    print "%d number of %s found" % (rs['hits']['total'], fieldnames[i])
    for hit in rs['aggregations']['length']['buckets']:
        lengths[fieldnames[i]][hit['key']] = hit['doc_count']
    missing = es.count(index='patents', doc_type='patent', body=missing_query)['count']
    print "%d number of missing %s" % (missing, fieldnames[i])

for name in fieldnames:
    df = pd.DataFrame(lengths[name].items())
    plt.plot(df[0], df[1])
    plt.xlabel(name + ' lengths')
    plt.show()

