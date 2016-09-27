shinyUI(bootstrapPage(
  numericInput(inputId='TopicVal',
               label='Topic Choice',
               min = 1, max = 100,value=1),
  
  checkboxInput(inputId = "slider",
                label = strong("Show Slider"),
                value = FALSE),
  
  conditionalPanel(condition = "input.slider == true",
    sliderInput(inputId = "TopicVal2",
                label = "Topic Choice",
                min = 1, max = 400, value = 1, step = 1)),

  selectInput(inputId='k',
                label='Number of Words',
                choices = c(10, 20, 30,40, 50,75,100),
                selected=20),    
  
  plotOutput(outputId = "main_plot", height = "300px")
  
  )
  
)