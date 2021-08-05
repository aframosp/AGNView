# Step-By-Step

This file works as a Table of contents (TOC) to follow the procedures done to reproduce the information presented in the paper. The numbers on this TOC are the same as in the [Jupyter notebooks](../Notebooks). Each subseccion related to a [Data](../Data), [Additional](../Additionals) or [Figure](../Figures) file is indicated with a '=>'. It is important to keep in mind that one of the steps is not included in this repository (Step 5, where we run the [CIGALE](https://cigale.lam.fr/) modelling in the [Peregrine cluster](https://www.rug.nl/society-business/centre-for-information-technology/research/services/hpc/facilities/peregrine-hpc-cluster?lang=en)). The information created at that step is located in a [Zenodo repositoty](https://doi.org/10.5281/zenodo.NNNNNNN), where we add a script to generate the SEDs for a given galaxy inside the Seyfert Sample. 

## TOC
1) [Create the Database Sample](../Notebooks/1_Obtain_Seyfert_Samples.ipynb)
* 1.1 Obtain a list of Seyfert galaxies from [SIMBAD TAP](https://simbad.u-strasbg.fr/simbad/sim-tap) => [SMB_Dec_03_2020.csv](../Data/Raw)
* 1.2 Use astropy (or [TOPCAT](http://www.star.bris.ac.uk/~mbt/topcat/)) to cross-match [SIMBAD](http://simbad.u-strasbg.fr/simbad/) galaxies and [VCV](https://ui.adsabs.harvard.edu/abs/2010A%26A...518A..10V/abstract) Galaxies => [SMB_VCV_Dec_03_2020.csv](../Data/Raw)
* 1.3 Obtain the bibcodes for the otype classifications in SIMBAD => [BibcodesOtypes_Dec_03_2020.csv](../Data/Raw)
2) [Clean the Seyfert Sample](../Notebooks/2_Clean_Sample.ipynb)
* 2.1 Remove different redshifts [**FIGURE 1**](../Figures/F1.pdf)
* 2.2 Separate the origin of the bibcode
* 2.3 Dealing with UNK bibcodes and Seyfert Types => [NLS1_reclass.txt](../Data/Complementary)
* 2.4 Create the final sample of galaxies in terms of redshift and bibcodes => [VCV_SMB_otypes.txt](../Data/Final)
* 2.5 Calculate the final numbers from the otypes TABLE 3
3) [Obtain the SEDs for Database Sample](../Notebooks/3_Obtain_SEDs.ipynb) (with a simplified [Python script](/Additionals/3_Obtain_SEDs.py))
* 3.1 Get SEDs from [CDS](https://cds.u-strasbg.fr/) and [NED](https://ned.ipac.caltech.edu/) with their respective bibcodes [Bibcodes_SED.csv](../Data/Interim) and eliminate duplicate measurements 
* 3.2 Select photometric filters/bands
* 3.3 Save => [SEDs](../Data/Interim) for each galaxy
4) [Create CIGALE Photometry file for Database Sample](../Notebooks/4_Create_CIGALEPhot.ipynb)
* 4.1 Create equivalencies between NED and CDS tables
* 4.2 Transform photometry to CIGALE photometry file
* 4.3 Clean photometry points
* 4.4 Remove galaxies taking into account energy balance, at least 2 IR bands and 5 Opt bands => [CIGPhot_BadEnergyBalance.tbl](../Data/Complementary)
* 4.5 Separating galaxies at different redshifts: Split in ten groups of redshifts
* 4.6 Create CIGALE photometry files => [CIGPhot_EnergyBal_NN.tbl](../Data/Interim/PhotometryFiles) and [CIGPhot_EnergyBal_All.tbl](../Data/Final)
5) Run CIGALE with the parameters in TABLE 2 => [CIGALEOutputs](../Data/Interim/CIGALEOutputs)
* 5.1 Run Fritz models Fr
* 5.2 Run SKIRTOR models SK
* 5.3 Run Fritz and SKIRTOR models but only with two angles 30 and 70.
* 5.4 Run Fr and SK for fAGN=0, this two should give the same results
6) [Calculate the initial numbers of the sample used](../Notebooks/6_Initial_Numbers.ipynb)
* 6.1 Numbers from photometry TABLE 1
* 6.2 Numbers from VCV TABLE 3 
* 6.3 Numbers from SMB TABLE 3 
* 6.4 Numbers in both SMB and VCV, part of the values for TABLE 3 
7) [Join and clean CIGALE results](../Notebooks/7_Clean_CIGALE_results.ipynb)
* 7.1 Join the ten redshift groups runs in one table
* 7.2 Red-chi-square distributions [**FIGURE 3**](../Figures/F3.pdf)
* 7.3 Cleaning and save files => [Cleanresults_*.fits](../Data/Final/CIGALEOutputs)
* 7.4 Calculate the counts for galaxy type TABLE 3 
8) [Example SEDs for SKIRTOR and Fritz](../Notebooks/8_SED_Plots.ipynb)
* 8.1 Select best and worst SED fittings => [*best_model.fits](../Data/Complementary/ExampleSEDs)
* 8.2 Plot the 4 SEDs for the best galaxy [**FIGURE 2**](../Figures/F2.pdf) and the worst galaxy   
9) [Verification with other estimations](../Notebooks/9_Verification_Estimations.ipynb)
* 9.1 Obtain the data from [Vika et al.(2017)](https://ui.adsabs.harvard.edu/abs/2017A%26A...597A..51V/abstract) 
* 9.2 Compare the parameters [**FIGURE 4**](../Figures/F4.pdf)
10) [Pre-Analyse of data](../Notebooks/10_PreAnalysis.ipynb)
* 10.1 Join clean results
* 10.2 Experiments with the parameters of the classifiers, assuming both classifications
* 10.3 Use [GridSearchCV](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.GridSearchCV.html) to find parameters for the classifiers   
11) [Analyse the results with Tables](../Notebooks/11_Analysis_Tables.ipynb)
* 11.1 Join clean results
* 11.2 Feature selection using [RFECV](https://scikit-learn.org/stable/modules/generated/sklearn.feature_selection.RFECV.html) [**FIGURE 5**](../Figures/F5.pdf)
* 11.3 Correlation-scores in the classification task with viewing angle and AGN disc luminosity TABLE 4
* 11.4 Correlation-scores in the classification task with ML TABLE 4
* 11.5 Predict classifications for S and SyG type galaxies TABLE 5          
12) [Analyse the results with Plots](../Notebooks/12_Analysis_Plots.ipynb)
* 12.1 Join clean results and transform to be used in the plots
* 12.2 Compare physical parameters from Fritz and SKIRTOR models [**FIGURE 6**](../Figures/F6.pdf)
* 12.3 Compare difference in physical parameters with Type. We use both SMB and VCV classifications so Type-1=Sy1 and Type-2=Sy2 [**FIGURE 7**](../Figures/F7.pdf). Additionally we compare the classifications also with the 30/70 model [**FIGURE ALT 7**](../Figures/F7_Alt.pdf)
* 12.4 Compare other VCV classifications as S1.0, S1.2, S1.5, S1.8, S1.9 [**FIGURE 8**](../Figures/F8.pdf) with SKIRTOR model
* 12.5 Redshift evolution of physical parameters [**FIGURE 9**](../Figures/F9.pdf)
* 12.6 Accretion power (intrinsic luminosity of the disc AGN luminosity) for the different setups [**FIGURE 10**](../Figures/F9.pdf)
  
A1. [Verification of the narrow-line Seyfert 1 galaxies](../Notebooks/A1_NarrowLineS1.ipynb)
* A1.1 Join information
* A1.2 Comparing AGN parameters [**FIGURE A1**](../Figures/A1.pdf)