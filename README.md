# Reproduction repository for "The viewing angle in AGN SED models, a data-driven analysis"

=======

This repository contains data and code to reproduce the results of the paper "The viewing angle in AGN SED models, a data-driven analysis"(add link). Each step of the work is described in a [step-by-step](/Data/Additionals/StepByStep.md) file with their respective [Jupyter notebooks](/Notebooks). 

For any questions or remarks, contact: [a.f.ramos.padilla@sron.nl](mailto:a.f.ramos.padilla@sron.nl)

Some re-runs in the notebooks are needed to verify everything is working correctly. LICANSE and Citation files are missing as well.


## Software requirements

These are the most important software packages to work with the files. We print all the packages in a given notebook using the IPython magic extension [watermark](https://github.com/rasbt/watermark). We also use [autotpep8](https://pypi.org/project/autopep8/) to format the code to the PEP 8 style guide. 

* [CIGALE](https://cigale.lam.fr/)???
* Python (we ignore standard libraries)
    * [astropy](https://github.com/astropy/astropy)
    * [pandas](https://pandas.pydata.org/)
    * [numpy](https://numpy.org/)
    * [matplotlib](https://matplotlib.org/)
    * [astroquery](https://astroquery.readthedocs.io/en/latest/)
    * [scipy](https://www.scipy.org/)
    * [sklearn](https://scikit-learn.org/stable/index.html)
    * [seaborn](https://seaborn.pydata.org/index.html)
    * [xgboost](https://xgboost.readthedocs.io/en/latest/)
    * [requests](https://docs.python-requests.org/en/master/)

## Content

* [Data](/Data): Most of the data related with the paper.
* [Figures](/Figures): Figures presented in the paper.
* [Notebooks](/Notebooks): Most of the code to generate data and figures (includes the extensions .ipynb, .html and .pdf)
* [Additionals](/Additionals): Folder containing the step-by-step description and a auxiliary Python script.  