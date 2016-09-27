library(tm)
library(RTextTools)
library(topicmodels)
data(NYTimes)
ttl_corpus <-  create_matrix(NYTimes$Title,
                                 language='english',
                                 removeNumbers=TRUE,
                                 stemWords=TRUE,
                                 removePunctuation=TRUE,
                                 weighting=weightTf, #weightTfIdf
                                 toLower=TRUE,
                                 stripWhitespace=TRUE,
                                 minWordLength=3,
                                 ngramLength=1,
                                 minDocFreq=2)
inspect(ttl_corpus[1:5,1:5])
trs <- slam::row_sums(ttl_corpus,na.rm=T)
tdtm   <- ttl_corpus[trs> 0, ]  
ttl_lda <- LDA(tdtm,20)
# Prints the most probable term per topic
terms(ttl_lda)
# Prints the summary table of how many documents are in each term
table(topics(ttl_lda))
