# ENGIE4800 - Data Science Capstone

This is the code/work to replicate the topic model my classmates and I built for Latent Patent Classification. An additional write up on the Columbia Data Science website can be found [here](https://industry.datascience.columbia.edu/project/mapping-us-patent-applications).

**Contributors:**

Name | GitHub Username | Email 
---  | ---      | --- 
Abdus Khan |  @akhan3674 | k3674@columbia.edu
Francisco Arceo |  @franciscojavierarceo | fja2114@columbia.edu
Gabrielle Agrocostea | @gabya06 | gda208@columbia.edu
Justin Law | @totakeke | jhl2184@columbia.edu
Tony Paek | @tonypaek | sp3298@columbia.edu

----------------
### Stages
----------------

	1. Data Acquisition and Parsing
		a. Downloading datasets
		b. Parsing data to find metadata
			- Requires subsetting fields 
			- Requires subsetting data to utility patents
	2. Exploratory Data analysis and model selection
		a. This is the phase in which we begin to use various unsupervised learning methods to classify data
		b. A few options for modeling are below
			- Correlated Topic Models
			- Discrete Infinite Logistic Normal Distribution DILN (Pronounced DILYN)
			- Dynamic Topic Models
	3. Implementation and evaluation
		a. We will have to have an evaluation metric for the modeling stage in step 2
		b. We should also consider designing an application to show the output from the analysis in an intuitive way


