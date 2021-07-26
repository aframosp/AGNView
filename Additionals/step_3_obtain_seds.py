#!/usr/bin/env python
# coding: utf-8
# pylint: disable=no-member
""" Code to obtain the SEDS with a terminal. For more information check the notebook """

import time
from os import path
from pathlib import Path
from datetime import datetime

import astropy.units as u
from astropy.table import Table, vstack, unique

from astroquery.ned import Ned
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from astroquery.ned.core import RemoteServiceError, TableParseError

import requests
from requests import Request, Session

import matplotlib.pyplot as plt
import numpy as np
from numpy import unique as uniq

print('File reading ...')
Sample = Table.read('../Data/Final/VCV_SMB_otype.txt', format='ascii')
print('File VCV_TAP.txt ready')


class ObtainPhotometry:
    """This class allows us to download the SEDs from NED and SIMBAD"""

    def __init__(self, name, url):
        self.name = name
        self.cds_url = url
        self.tmp_cds = '../Data/Interim/CDSVotables/'
        self.tmp_ned = '../Data/Interim/NEDVotables/'
        Path(self.tmp_cds).mkdir(parents=True, exist_ok=True)
        Path(self.tmp_ned).mkdir(parents=True, exist_ok=True)
        print('Working on galaxy ', self.name)
        self.obtain_vot()
        self.read_votable()
        self.add_bibcode_cds()
        self.check_both_tables()

    def check_vot(self):
        """Check that the content of the votable is ok"""
        vot_bad = True
        while vot_bad:
            try:
                self.cds_table = Table.read(self.tmp_cds+self.name+'.vot',
                                            format='votable')
                print('Votable checked')
                vot_bad = False
            except (ValueError, FileNotFoundError):
                print('Error in votable, deleting content-length')
                ses = Session()
                req_p = Request('POST', self.cds_url)
                prepped = req_p.prepare()
                del prepped.headers['content-length']
                ses.send(prepped)
                self.request_url()

    def request_url(self):
        """Request content (votable) from url"""
        req = requests.get(self.cds_url,
                           headers={'cache-control': 'private, max-age=0, no-cache',
                                    "Pragma": "no-cache"})
        if req.status_code == 200:
            with open(self.tmp_cds+self.name+'.vot', 'wb') as f_vot:
                f_vot.write(req.content)
                f_vot.close()

    def obtain_vot(self):
        """Function to obtain the VOTables"""
        print(datetime.now(), 'Get SEDs')
        if path.exists(self.tmp_cds+self.name+'.vot'):
            print('Reading CDS file')
        else:
            #             time.sleep(4)  # This is used to avoid being flag by the server
            print(self.cds_url)
            self.request_url()
            self.check_vot()
        print(datetime.now(), 'Got CDS SED')
        self.ned_flag = False
        if path.exists(self.tmp_ned+self.name+'.vot'):
            print('Reading NED file')
        else:
            #             time.sleep(0.5)
            other_ids = Simbad.query_objectids(self.name)
            for gal_id in other_ids['ID']:
                try:
                    ned_tab = Ned.get_table(gal_id, table='photometry')
                    # Use just photometry by using the units in Jy
                    ned_tab[ned_tab['NED Units'] == 'Jy'].write(self.tmp_ned+self.name+'.vot',
                                                                 format='votable')
                    print(datetime.now(), 'Got NED SED')
                    break
                except (RemoteServiceError, TableParseError):
                    if gal_id == other_ids['ID'][-1]:
                        self.ned_flag = True
                    continue
                except IndexError:
                    self.ned_flag = True

    def read_votable(self):
        """Function to read the VOTables"""
        self.cds_table = Table.read(self.tmp_cds+self.name+'.vot',
                                    format='votable')
        if self.ned_flag:
            print('No NED Table')
            self.ned_table = Table(names=['Refcode', 'Flux_Density', 'Observed_Passband',
                                          'Frequency', 'NED_Uncertainty'], masked=True)
        else:
            self.ned_table = Table.read(self.tmp_ned+self.name+'.vot',
                                        format='votable')

    def plot_sed(self):
        """In case we want to plot the SED"""
        plt.scatter(self.cds_table['sed_freq'].to(u.micron, equivalencies=u.spectral()),
                    self.cds_table['sed_flux'], label='CDS')
        plt.scatter(self.ned_table['Frequency'].to(u.micron, equivalencies=u.spectral()),
                    self.ned_table['Flux_Density'], marker='*', label='NED')
        plt.loglog()
        plt.xlabel('Wavelength [um]')
        plt.ylabel('Flux [Jy]')
        plt.legend()

    def add_bibcode_cds(self):
        """Adding the Bibcode to the CDS tables"""
        self.cds_table['Bibcode'] = np.array(['Empty']*len(self.cds_table),
                                             dtype='object')
        for tabindx, tabinfo in enumerate(self.cds_table['_tabname']):
            try:
                time.sleep(0.001)  # This is used to avoid being flag by the server
                name_cat = tabinfo.rpartition('/')[0]
                search = Vizier.query_constraints(catalog='METAcat', name=name_cat)
                self.cds_table['Bibcode'][tabindx] = search[0][0]['bibcode']
            except IndexError:
                print('There is an error at ', tabindx, tabinfo)

    def check_both_tables(self):
        """Check the rows of CDS and NED and remove all duplicates in the photometric bands"""
        to_rem = []
        for u_refcode in np.unique(self.ned_table['Refcode']):
            l_cds = np.where(self.cds_table['Bibcode'] == u_refcode)[0]#.decode('utf-8'))[0]
            l_ned = np.where(self.ned_table['Refcode'] == u_refcode)[0]
            if len(l_cds) > 0 and len(l_ned) > 0:
                print('Duplicate!')
                for lcds in l_cds:
                    for lned in l_ned:
                        flx_ned = str(self.ned_table[lned]['Flux_Density'])
                        flx_cds = str(self.cds_table[lcds]['sed_flux'])
                        if flx_ned == flx_cds:
                            print('Deleting NED filter ',
                                  self.ned_table[lned]['Observed_Passband'],
                                  ' with Bibcode ',
                                  self.ned_table[lned]['Refcode'])
                            to_rem.append(lned)
        self.ned_table.remove_rows(to_rem)


CDSFilters = ['GALEX:FUV', 'GALEX:NUV',
              "SDSS:u'", "SDSS:g'", "SDSS:r'", "SDSS:i'", "SDSS:z'",
              'SDSS:u', 'SDSS:g', 'SDSS:r', 'SDSS:i', 'SDSS:z',
              '2MASS:J', '2MASS:H', '2MASS:Ks',
              ':=3.6um', ':=4.5um', ':=5.8um', ':=8um',
              'WISE:W1', 'WISE:W2', 'WISE:W3', 'WISE:W4',
              'IRAS:12', 'IRAS:25', 'IRAS:60', 'IRAS:100',
              'Spitzer/MIPS:24', 'Spitzer/MIPS:70', 'Spitzer/MIPS:160',
              'Herschel/PACS:70', 'Herschel/PACS:100', 'Herschel/PACS:160',
              'Herschel/SPIRE:250', 'Herschel/SPIRE:350', 'Herschel/SPIRE:500',
              ':=250um', ':=350um', ':=500um',
              ':=1.4GHz', ':=21cm', ':=1.5GHz', ':=20cm', ':=5GHz', ':=6cm']

NEDFilters = ['2-10 keV (XMM)', '0.5-2 keV (XMM)',
              'FUV (GALEX)', 'NUV (GALEX)',
              'u (SDSS) AB', 'g (SDSS) AB', 'r (SDSS) AB', 'i (SDSS) AB', 'z (SDSS) AB',
              'J (2MASS) AB', 'H (2MASS) AB', 'Ks (2MASS) AB',
              'W1 (WISE)', 'W2 (WISE)', 'W3 (WISE)', 'W4 (WISE)',
              '3.6 microns (IRAC)', '4.5 microns (IRAC)',
              '5.8 microns (IRAC)', '8.0 microns (IRAC)',
              '12 microns (IRAS)', '25 microns (IRAS)',
              '60 microns (IRAS)', '100 microns (IRAS)',
              '24 microns (MIPS)', '70 microns (MIPS)', '160 microns (MIPS)',
              '70 microns (PACS)', '100 microns (PACS)', '160 microns (PACS)',
              '250 microns (SPIRE)', '350 microns (SPIRE)', '500 microns (SPIRE)',
              '4.89 GHz (VLA)', '1.46 GHz (VLA)', '1.4GHz']


def clean_cds_to(table):
    """Remove rows with masked (empty) and null (0) values, then average the values."""
    table.remove_rows(np.where(table['sed_eflux'].mask)[0])
    table.remove_rows(np.where(table['sed_eflux'] == 0.0)[0])
    values, counts = uniq(table['sed_flux'], return_counts=True)
    if len(values) > 0:
        avg = np.average(values, weights=counts)
        std = np.sqrt(np.sum(table['sed_eflux']**2))
        return(avg, std)
    return(np.nan, np.nan)

def clean_ned_to(table):
    """Remove rows with masked (empty) and string values, then average the values."""
    table.remove_rows(np.where(table['Flux_Density'].mask)[0])
    table.remove_rows(np.where(table['NED_Uncertainty'] == '')[0])
    table.remove_rows(np.where(table['NED_Uncertainty'] == '+/-...')[0])
    values, counts = uniq(table['Flux_Density'], return_counts=True)
    table['NED_Uncertainty'] = [float(j.split('+/-')[-1]) for j in table['NED_Uncertainty']]
    if len(values) > 0:
        avg = np.average(values, weights=counts)
        std = np.sqrt(np.sum(table['NED_Uncertainty']**2))
        return(avg, std)
    return(np.nan, np.nan)

class CleanPhotometry:
    """Clean the photometry in CDS and NED tables"""
    def __init__(self, table_cds, table_ned):
        print('Cleaning')
        self.cds_table = table_cds
        self.ned_table = table_ned
        self.bib_codes = np.array([])
        self.join_tables()
        
    def get_bibcodes(self, bibcode):
        """Get the bibcodes for the tables to analyse them later."""
        bib = np.array(bibcode)
        self.bib_codes = np.unique(np.concatenate((self.bib_codes, bib)))
    
    def clean_cds_to(self, table):
        """Remove rows with masked (empty) and null (0) values, then average the values."""
        table.remove_rows(np.where(table['sed_eflux'].mask)[0])
        table.remove_rows(np.where(table['sed_eflux'] == 0.0)[0])
        self.get_bibcodes(table['Bibcode'])
        values, counts = uniq(table['sed_flux'], return_counts=True)
        if len(values) > 0:
            avg = np.average(values, weights=counts)
            std = np.sqrt(np.sum(table['sed_eflux']**2))
            return(avg, std)
        return(np.nan, np.nan)

    def clean_ned_to(self, table):
        """Remove rows with masked (empty) and string values, then average the values."""
        table.remove_rows(np.where(table['Flux_Density'].mask)[0])
        table.remove_rows(np.where(table['NED_Uncertainty'] == '')[0])
        table.remove_rows(np.where(table['NED_Uncertainty'] == '+/-...')[0])
        self.get_bibcodes(table['Refcode'])
        values, counts = uniq(table['Flux_Density'], return_counts=True)
        table['NED_Uncertainty'] = [float(j.split('+/-')[-1]) for j in table['NED_Uncertainty']]
        if len(values) > 0:
            avg = np.average(values, weights=counts)
            std = np.sqrt(np.sum(table['NED_Uncertainty']**2))
            return(avg, std)
        return(np.nan, np.nan)

    def filters_ned(self, table_filter):
        """ Use only the information that we need from NED """
        data_tab = []
        band = [np.where(self.ned_table['Observed_Passband'] == filt)[0] for filt in table_filter]
        for bandinx, bandif in enumerate(band):
            avg, std = self.clean_ned_to(self.ned_table[bandif])
            if np.isnan(avg):
                continue
            to_um = self.ned_table[bandif]['Frequency'].to(u.micron,
                                                           equivalencies=u.spectral())
            data_tab.append([table_filter[bandinx], np.mean(to_um), avg*u.Jy, std*u.Jy])
        return(Table(np.array(data_tab),
                     names=['Filter', 'Wave', 'Flux', 'F_er'],
                     dtype=('U32', 'float64', 'float64', 'float64')))

    def filters_cds(self, table_filter):
        """Use only the information that we need from CDS"""
        data_tab = []
        band = [np.where(self.cds_table['sed_filter'] == filt)[0] for filt in table_filter]
        for bandinx, bandif in enumerate(band):
            avg, std = self.clean_cds_to(self.cds_table[bandif])
            if np.isnan(avg):
                continue
            to_um = self.cds_table[bandif]['sed_freq'].to(u.micron,
                                                          equivalencies=u.spectral())
            data_tab.append([table_filter[bandinx], np.mean(to_um), avg*u.Jy, std*u.Jy])
        return(Table(np.array(data_tab),
                     names=['Filter', 'Wave', 'Flux', 'F_er'],
                     dtype=('U32', 'float64', 'float64', 'float64')))

    def join_tables(self):
        """Finally, we join the tables and remove those whose errors are too high"""
        self.final_tab = vstack([self.filters_cds(CDSFilters), self.filters_ned(NEDFilters)])
        self.final_tab.remove_rows(np.where(self.final_tab['F_er']/self.final_tab['Flux'] >= 1))

INIT_URL = 'http://vizier.u-strasbg.fr/viz-bin/sed?-c='
urls = [INIT_URL+str(Sample['ra'][row])+'%20' +
        str(Sample['dec'][row])+'&-c.rs=5' for row in range(len(Sample))]
Sample['cds_url'] = urls        

# We show an example of the last galaxies from the positon 17725
IND = 4152  # It should be zero for all, here is 17725 as an example
SED_PATH = '../Data/Interim/SEDs/'
Path(SED_PATH).mkdir(parents=True, exist_ok=True)
for Galaxy, cds_url in Sample['main_id','cds_url'][IND:]:
    if path.exists(SED_PATH+Galaxy+'_Phot.txt'):
        print(IND, 'Already exist')
        IND += 1
        continue
    InitTabl = ObtainPhotometry(Galaxy, cds_url)
    cleaned = CleanPhotometry(InitTabl.cds_table, InitTabl.ned_table)
    SED = cleaned.final_tab
    BIBCODES = ';'.join(cleaned.bib_codes)
    with open("../Data/Interim/Bibcodes_SED.csv", "a+") as file_bibcodes:
        file_bibcodes.writelines([Galaxy+',', BIBCODES+'\n'])
        file_bibcodes.close()
    SED.write(SED_PATH+Galaxy+'_Phot.txt', format='ascii')
    print(IND, 'Finish')
    IND += 1
