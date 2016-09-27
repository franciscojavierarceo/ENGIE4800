library(stringr)
if( sum(regexpr('Rtopicdata2015_1019_2222.RData',dir())>0)==0){
  df1 <- read.csv('/Users/franciscojavierarceo/GitHub/patents/Code/2014/out/PythonLDA2015_1019_2222.csv',
                  sep='|',header=F,stringsAsFactors=F)
#   df1 <- read.csv('/Users/franciscojavierarceo/GitHub/patents/Code/test/CSV/PythonLDA.csv',
#                   sep='|',header=F,stringsAsFactors=F)
  clean <- function(x,val){
    y <- unlist(strsplit(str_replace_all(x, "\\+", " "),' '))
    y <-  y[nchar(y)>0]
    p <- c()
    w <- c()
    for(i in 1:length(y)){
      p[i] <- strsplit(y,'\\*')[[i]][1]
      w[i] <- strsplit(y,'\\*')[[i]][2]
    }
    p <- as.numeric(p)
    return(data.frame(Probability=p,Word=w,Topic=paste("Topic",val,sep='_')))
  }
  
  out <- list()
  for(i in 1:nrow(df1)){
    out[[i]] <- clean(df1[i,],i)
  }
  final <- out[[1]]
  for(i in 2:length(out)){
    final <- rbind(final,out[[i]])
  }
  save(final,file='Rtopicdata2015_1019_2222.RData')  
} else {
  load('Rtopicdata2015_1019_2222.RData')  
}
