#!/usr/bin/env python
# coding: utf-8
# pylint: disable=no-member
""" Code to obtain the SEDS with a terminal. For more information check the notebook """

import time
from datetime import datetime
from os import path

import astropy.units as u
from astropy.table import Table, vstack

from astroquery.ned import Ned
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

import requests

import matplotlib.pyplot as plt
import numpy as np
from numpy import unique as uniq

print('File reading ...')
Sample = Table.read('../Data/Final/VCV_SMB_otype.txt', format='ascii')
print('File VCV_TAP.txt ready')


class ObtainPhotometry:
    """This class allows us to download the SEDs from NED and SIMBAD"""
    def __init__(self, Name):
        self.name = Name
        self.tmp_cds = '../Data/Interim/CDSVotables/'
        self.tmp_ned = '../Data/Interim/NEDVotables/'
        print('Working on galaxy ', self.name)
        self.obtain_vot()
        self.read_votable()
        self.add_bibcode_cds()
        self.check_both_tables()

    def obtain_vot(self):
        """Function to obtain the VOTables"""
        print(datetime.now(), 'Get CDS SED')
        if path.exists(self.tmp_cds+self.name+'.vot'):
            print('Reading CDS file')
        else:
            time.sleep(5)  # This is used to avoid being flag by the server
            galaxy_smb = Simbad.query_object(self.name)
            ras = galaxy_smb[0]['RA'].replace(' ', '%20')
            dec = galaxy_smb[0]['DEC'].replace(' ', '%20')
            irl = 'http://vizier.u-strasbg.fr/viz-bin/sed?-c=' + \
                str(ras)+'%20'+str(dec)+'&-c.rs=5'
            print(irl)
            req = requests.get(irl)
            open(self.tmp_cds+self.name+'.vot', 'wb').write(req.content)
        print(datetime.now(), 'Got CDS SED')
        self.ned_flag = False
        if path.exists(self.tmp_ned+self.name+'.vot'):
            print('Reading NED file')
        else:
            #             time.sleep(0.5)
            try:
                ned_tab = Ned.get_table(self.name, table='photometry')
                # Use just photometry by using the units in Jy
                ned_tab[ned_tab['NED Units'] == b'Jy'].write(self.tmp_ned+self.name+'.vot',
                                                             format='votable')
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
                name_cat = tabinfo.rpartition('/')[0]
                search = Vizier.query_constraints(catalog='METAcat', name=name_cat)
                self.cds_table['Bibcode'][tabindx] = search[0][0]['bibcode']
            except IndexError:
                print('There is an error at ', tabindx, tabinfo)

    def check_both_tables(self):
        """Check the rows of CDS and NED and remove all duplicates in the photometric bands"""
        to_rem = []
        for u_refcode in np.unique(self.ned_table['Refcode']):
            l_cds = np.where(self.cds_table['Bibcode'] == u_refcode.decode('utf-8'))[0]
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

NEDFilters = [b'2-10 keV (XMM)', b'0.5-2 keV (XMM)',
              b'FUV (GALEX)', b'NUV (GALEX)',
              b'u (SDSS) AB', b'g (SDSS) AB', b'r (SDSS) AB', b'i (SDSS) AB', b'z (SDSS) AB',
              b'J (2MASS) AB', b'H (2MASS) AB', b'Ks (2MASS) AB',
              b'W1 (WISE)', b'W2 (WISE)', b'W3 (WISE)', b'W4 (WISE)',
              b'3.6 microns (IRAC)', b'4.5 microns (IRAC)',
              b'5.8 microns (IRAC)', b'8.0 microns (IRAC)',
              b'12 microns (IRAS)', b'25 microns (IRAS)',
              b'60 microns (IRAS)', b'100 microns (IRAS)',
              b'24 microns (MIPS)', b'70 microns (MIPS)', b'160 microns (MIPS)',
              b'70 microns (PACS)', b'100 microns (PACS)', b'160 microns (PACS)',
              b'250 microns (SPIRE)', b'350 microns (SPIRE)', b'500 microns (SPIRE)',
              b'4.89 GHz (VLA)', b'1.46 GHz (VLA)', b'1.4GHz']


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
    table.remove_rows(np.where(table['NED_Uncertainty'] == b'')[0])
    table.remove_rows(np.where(table['NED_Uncertainty'] == b'+/-...')[0])
    values, counts = uniq(table['Flux_Density'], return_counts=True)
    table['NED_Uncertainty'] = [float(j.split(b'+/-')[-1]) for j in table['NED_Uncertainty']]
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
        self.join_tables()



    def filters_ned(self, table_filter):
        """ Use only the information that we need from NED """
        data_tab = []
        band = [np.where(self.ned_table['Observed_Passband'] == filt)[0] for filt in table_filter]
        for bandinx, bandif in enumerate(band):
            avg, std = clean_ned_to(self.ned_table[bandif])
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
            avg, std = clean_cds_to(self.cds_table[bandif])
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

# In case the connection is lost we will use IND as our initial point
IND = 5460 # It should be zero for all, here is 5460 as an example
for Galaxy in uniq(Sample['main_id'])[IND:]:
    InitTabl = ObtainPhotometry(Galaxy)
    SED = CleanPhotometry(InitTabl.cds_table, InitTabl.ned_table).final_tab
    SED.write('../Data/Interim/SEDs/'+Galaxy+'_Phot.txt', format='ascii')
    IND += 1
    print(IND)
