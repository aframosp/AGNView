# Reproduction repository for "The viewing angle in AGN SED models, a data-driven analysis"

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/aframosp/AGNView/HEAD)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.5227294.svg)](https://doi.org/10.5281/zenodo.5227294)

This repository contains data and code to reproduce the results of the paper "The viewing angle in AGN SED models, a data-driven analysis". Each step of the work is described in a [step-by-step](/Additionals/StepByStep.md) file with their respective [Jupyter notebooks](/Notebooks). 

For any questions or remarks, contact: [ramos at astro.rug.nl](mailto:ramos@astro.rug.nl)


## Software requirements

The most important software packages to work with the files in this repository are in [environment.yml](environment.yml). This file is also used to launch a [Binder](https://mybinder.org/) to open the Jupyter notebooks interactively. We print all the packages in a given notebook using the IPython magic extension [watermark](https://github.com/rasbt/watermark). We also use [autotpep8](https://pypi.org/project/autopep8/) to format the code to the PEP 8 style guide. 

## Content

* [Data](/Data): Most of the data related with the paper.
* [Figures](/Figures): Figures presented in the paper.
* [Notebooks](/Notebooks): Most of the code to generate data and figures (includes the extensions .ipynb and .html)
* [Additionals](/Additionals): Folder containing the step-by-step description and an auxiliary Python script.
