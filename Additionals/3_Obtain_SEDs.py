#!/usr/bin/env python
# coding: utf-8

import time
import numpy as np

import astropy.units as u
from astropy.table import Table, vstack

from astroquery.ned import Ned
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

import requests
from os import path
from datetime import datetime
import matplotlib.pyplot as plt
from numpy import unique as uniq

print('File reading ...')
Sample = Table.read('../Data/Final/VCV_SMB_otype.txt', format='ascii')
print('File VCV_TAP.txt ready')


class ObtainPhotometry:
    """This class allows us to download the SEDs from NED and SIMBAD"""
    def __init__(self, Name, Smot=False):
        self.name = Name
        self.tmpCDS = '../Data/Interim/CDSVotables/'
        self.tmpNED = '../Data/Interim/NEDVotables/'
        print('Working on galaxy ', self.name)
        self.ObtainVot()
        self.ReadVotTables()
        self.AddBibcodeCDS()
        self.CheckBothTables()
#         self.PlotSED(Smot) ## Just when we want to see the SED

    def ObtainVot(self):
        """Function to obtain the VOTables"""
        print(datetime.now(), 'Get CDS SED')
        if path.exists(self.tmpCDS+self.name+'.vot'):
            print('Reading CDS file')
        else:
            time.sleep(5) ## This is used to avoid being flag by the server
            GalaxyS = Simbad.query_object(self.name)
            RA = GalaxyS[0]['RA'].replace(' ', '%20')
            DEC = GalaxyS[0]['DEC'].replace(' ', '%20')
            irl = 'http://vizier.u-strasbg.fr/viz-bin/sed?-c=' + \
                str(RA)+'%20'+str(DEC)+'&-c.rs=5'
            print(irl)
            r = requests.get(irl)
            open(self.tmpCDS+self.name+'.vot', 'wb').write(r.content)
        print(datetime.now(), 'Got CDS SED')
        self.NEDFlag = False
        if path.exists(self.tmpNED+self.name+'.vot'):
            print('Reading NED file')
        else:
            #             time.sleep(0.5)
            try:
                NEDTab = Ned.get_table(self.name, table='photometry')
                NEDTab[NEDTab['NED Units'] == b'Jy'].write(self.tmpNED+self.name+'.vot',
                                                           format='votable') # Use just photometry
            except:
                self.NEDFlag = True

    def ReadVotTables(self):
        """Function to read the VOTables"""
        self.CDSTable = Table.read(self.tmpCDS+self.name+'.vot',
                                   format='votable')
        if self.NEDFlag:
            print('No NED Table')
            self.NEDTable = Table(names=['Refcode', 'Flux_Density', 'Observed_Passband',
                                         'Frequency', 'NED_Uncertainty'], masked=True)
        else:
            self.NEDTable = Table.read(self.tmpNED+self.name+'.vot',
                                       format='votable')

    def PlotSED(self, smooth):
        """In case we want to plot the SED"""
        if smooth:
            self.SmoothSED()
            print(self.CDSTable.columns, self.NEDTable.columns)
        scatter(self.CDSTable['sed_freq'].to(u.micron, equivalencies=u.spectral()),
                self.CDSTable['sed_flux'], label='CDS')
        scatter(self.NEDTable['Frequency'].to(u.micron, equivalencies=u.spectral()),
                self.NEDTable['Flux_Density'], marker='*', label='NED')
        loglog()
        xlabel('Wavelength [um]')
        ylabel('Flux [Jy]')
        legend()

    def AddBibcodeCDS(self):
        """Adding the Bibcode to the CDS tables"""
        self.CDSTable['Bibcode'] = np.array(['Empty']*len(self.CDSTable),
                                            dtype='object')
        for tabindx, tabinfo in enumerate(self.CDSTable['_tabname']):
            try:
                Namcat = tabinfo.rpartition('/')[0]
                Search = Vizier.query_constraints(catalog='METAcat', name=Namcat)
                self.CDSTable['Bibcode'][tabindx] = Search[0][0]['bibcode']
            except:
                print('There is an error at ', tabindx, tabinfo)

    def CheckBothTables(self):
        """Check the rows of CDS and NED and remove all duplicates in the photometric bands"""
        ToRem = []
        for URefcode in np.unique(self.NEDTable['Refcode']):
            LCDS = np.where(self.CDSTable['Bibcode'] == URefcode.decode('utf-8'))[0]
            LNED = np.where(self.NEDTable['Refcode'] == URefcode)[0]
            if len(LCDS) > 0 and len(LNED) > 0:
                print('Duplicate!')
                for lcds in LCDS:
                    for lned in LNED:
                        if str(self.NEDTable[lned]['Flux_Density']) == str(self.CDSTable[lcds]['sed_flux']):
                            print('Deleting NED filter ',
                                  self.NEDTable[lned]['Observed_Passband'],
                                  ' with Bibcode ',
                                  self.NEDTable[lned]['Refcode'])
                            ToRem.append(lned)
        self.NEDTable.remove_rows(ToRem)

    def SmoothSED(self):
        """Create a smooth SED, only for plotting"""
        self.CDSTable = self.CDSTable.group_by('sed_freq').groups.aggregate(np.mean)
        self.NEDTable = self.NEDTable.group_by('Frequency').groups.aggregate(np.mean)


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
              b'3.6 microns (IRAC)', b'4.5 microns (IRAC)', b'5.8 microns (IRAC)', b'8.0 microns (IRAC)',
              b'12 microns (IRAS)', b'25 microns (IRAS)', b'60 microns (IRAS)', b'100 microns (IRAS)',
              b'24 microns (MIPS)', b'70 microns (MIPS)', b'160 microns (MIPS)',
              b'70 microns (PACS)', b'100 microns (PACS)', b'160 microns (PACS)',
              b'250 microns (SPIRE)', b'350 microns (SPIRE)', b'500 microns (SPIRE)',
              b'4.89 GHz (VLA)', b'1.46 GHz (VLA)', b'1.4GHz']


class CleanPhotometry:
    """Clean the photometry in CDS and NED tables"""
    def __init__(self, TableCDS, TableNED):
        print('Cleaning')
        self.CDSTable = TableCDS
        self.NEDTable = TableNED
        self.JoinTables()

    def CleanCDSTo(self, table):
        """Remove rows with masked (empty) and null (0) values, then average the values."""
        table.remove_rows(where(table['sed_eflux'].mask)[0])
        table.remove_rows(where(table['sed_eflux'] == 0.0)[0])
        Vales, counts = numpy.unique(table['sed_flux'], return_counts=True)
        if len(Vales) > 0:
            AVG = np.average(Vales, weights=counts)
            STD = np.sqrt(np.sum(table['sed_eflux']**2))
            return(AVG, STD)
        else:
            return(nan, nan)

    def CleanNEDTo(self, table):
        """Remove rows with masked (empty) and string values, then average the values."""
        table.remove_rows(where(table['Flux_Density'].mask)[0])
        table.remove_rows(where(table['NED_Uncertainty'] == b'')[0])
        table.remove_rows(where(table['NED_Uncertainty'] == b'+/-...')[0])
        Vales, counts = numpy.unique(table['Flux_Density'], return_counts=True)
        table['NED_Uncertainty'] = [float(j.split(b'+/-')[-1]) for j in table['NED_Uncertainty']]
        if len(Vales) > 0:
            AVG = np.average(Vales, weights=counts)
            STD = np.sqrt(np.sum(table['NED_Uncertainty']**2))
            return(AVG, STD)
        else:
            return(nan, nan)

    def FiltersNED(self, tableFilter):
        """ Use only the information that we need from NED """
        Tabls = []
        Band = [where(self.NEDTable['Observed_Passband'] == filt)[0] for filt in tableFilter]
        for bandinx, bandif in enumerate(Band):
            AVG, STD = self.CleanNEDTo(self.NEDTable[bandif])
            if isnan(AVG):
                continue
            else:
                Tabls.append([tableFilter[bandinx],
                              np.mean(self.NEDTable[bandif]['Frequency'].to(u.micron,
                                                                            equivalencies=u.spectral())),
                              AVG*u.Jy, STD*u.Jy])
        return(Table(array(Tabls),
                     names=['Filter', 'Wave', 'Flux', 'F_er'],
                     dtype=('U32', 'float64', 'float64', 'float64')))

    def FiltersCDS(self, tableFilter):
        """Use only the information that we need from CDS"""
        Tabls = []
        Band = [where(self.CDSTable['sed_filter'] == filt)[0] for filt in tableFilter]
        for bandinx, bandif in enumerate(Band):
            AVG, STD = self.CleanCDSTo(self.CDSTable[bandif])
            if isnan(AVG):
                continue
            else:
                Tabls.append([tableFilter[bandinx],
                              np.mean(self.CDSTable[bandif]['sed_freq'].to(u.micron,
                                                                           equivalencies=u.spectral())),
                              AVG*u.Jy, STD*u.Jy])
        return(Table(array(Tabls),
                     names=['Filter', 'Wave', 'Flux', 'F_er'],
                     dtype=('U32', 'float64', 'float64', 'float64')))

    def JoinTables(self):
        """Finally, we join the tables and remove those whose errors are too high"""
        self.TabFin = vstack([self.FiltersCDS(CDSFilters), self.FiltersNED(NEDFilters)])
        self.TabFin.remove_rows(where(self.TabFin['F_er']/self.TabFin['Flux'] >= 1))

ind = 5460  # In case the connection is lost we will use this as our initial point (5460 is an example)
for Galaxy in uniq(Sample['main_id'])[ind:]:
    InitTabl = ObtainPhotometry(Galaxy)
    SED = CleanPhotometry(InitTabl.CDSTable, InitTabl.NEDTable).TabFin
    SED.write('../Data/Interim/SEDs/'+Galaxy+'_Phot.txt', format='ascii')
    ind += 1
    print(ind)