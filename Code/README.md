# Code

This section will contain all of our code for the project

```
The code should be run in the following order:
	1. downloader.sh
	2. unzipfiles.sh
	3. DSGS_ParseData.py
	4. ldaModel.py
```

To run the ```downloader.sh``` file execute 
```
bash downloader.sh
bash unzipfiles.sh
python DSGS_ParseData.py [/InputDataPath/] [/OutputDataPath/]
```

Where ```[.]``` should be substituted with your local directories.

This works for a given directory, so all of the files should be available there, which needs to be modified slightly.

Next step is to full parallelize this operation, but it's much faster now.

**Note the DSGS_ParseData.py file is still not yet fully working, I need to do some debugging.**

To Run LDA Model:
```
python ldaModel.py /path/GS_Model.csv
```
We have a working version and the ShinApp is the Shiny Application that displays the top 10-50 words for each of the 200 topics of the first model.

This is the benchmark so far, and we still need to explore further solutions.

# Running the Shiny Application

In order to run the shiny application, you will have to (1) have RStudio, (2) have downloaded the *Shiny* library , and (3) download the ```ShinyApp.zip``` file from this repository. 

Then open the ```server.R``` file in RStudio and run click the *RunApp* function.

The application should run just fine after this. 
