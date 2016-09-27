library(ggplot2)
library(shiny)
source('LoadShinyData.R')
shinyServer(function(input, output) {
  output$main_plot <- renderPlot({
    tpc <- input$TopicVal
    if(input$slider){
      tpc <- input$TopicVal2
    }
    k <- input$k
    fss <- final[final$Topic==paste('Topic_',tpc,sep=''),]
    fss <- fss[order(-fss$Probability),]
    fss$Word <- factor(fss$Word,levels=fss$Word[order(fss$Probability)])
    ggplot(fss[1:k,],aes(x=Word,y=Probability))+ggtitle(paste('Topic',tpc))+
      geom_bar(stat='identity',position='dodge',fill='deepskyblue')+xlab('')+
      theme_bw()+coord_flip()+
      theme(axis.text.y = element_text(colour="grey20",size=20,angle=0,hjust=.5,vjust=.5,face="plain"),
            axis.text.x = element_text(colour="grey20",size=20,angle=0,hjust=.5,vjust=.5,face="plain"),
            axis.title.x = element_text(colour="grey20",size=20,angle=0,hjust=.5,vjust=.5,face="plain"))
    }, height = 900)    
  }
)
