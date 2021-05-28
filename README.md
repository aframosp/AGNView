# Reproduction repository for "The viewing angle in AGN SED models, a data-driven analysis"

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/aframosp/AGNView/HEAD)

This repository contains data and code to reproduce the results of the paper "The viewing angle in AGN SED models, a data-driven analysis"(add link). Each step of the work is described in a [step-by-step](/Data/Additionals/StepByStep.md) file with their respective [Jupyter notebooks](/Notebooks). 

For any questions or remarks, contact: [a.f.ramos.padilla@sron.nl](mailto:a.f.ramos.padilla@sron.nl)

**Some re-runs in the notebooks are needed to verify everything is working correctly. LICENSE and Citation files are missing as well.**


## Software requirements

The most important software packages to work with the files in this repository are in [environment.yml](environment.yml). This file is also used to launch a Binder to open the Jupyter notebooks interactively. We print all the packages in a given notebook using the IPython magic extension [watermark](https://github.com/rasbt/watermark). We also use [autotpep8](https://pypi.org/project/autopep8/) to format the code to the PEP 8 style guide. 

## Content

* [Data](/Data): Most of the data related with the paper.
* [Figures](/Figures): Figures presented in the paper.
* [Notebooks](/Notebooks): Most of the code to generate data and figures (includes the extensions .ipynb and .html)
* [Additionals](/Additionals): Folder containing the step-by-step description and an auxiliary Python script.