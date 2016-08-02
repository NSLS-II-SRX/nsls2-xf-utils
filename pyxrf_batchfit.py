# -*- coding: utf-8 -*-
"""
Created on Fri Oct 23 18:16:32 2015

@author: xf05id1
"""

from enaml import qt
import pyxrf.model.fit_spectrum as fits
fits.fit_pixel_data_and_save??

#wd = '/nfs/xf05id1/data/pyxrf_analysis/2015cycle3/300226_Hesterberg/'
#wd = '/nfs/xf05id1/userdata/2016_cycle1/300372_Gallaway/'
wd = '/nfs/xf05id1/userdata/2016_cycle1/300388_Thieme/xrfdata/batch_area2/'



#actualElist=[]
#fileprefixList=[]

#1775-1840
#first=1775
#last=1840
first = 2378
last = 2381

#'scan'+str(scanid)+'323AC1_XRF'
#eng = 15.0

fittingpara = '32416-XRF-fitforKaren'
fittingpara = 'scan2357_CottonSwipeArea1_tile1_fittingpara'

for i in range(last-first):                                                      
#    filen = 'scan'+str(scanid)+'323AC1_XRF'
    filen = str(scanid)+'.h5'
    fits.fit_pixel_data_and_save(wd, filen, param_channel_list=['2015_11_13_22_45_pyxrf_ch1_fitpara.json',  '2015_11_13_22_45_pyxrf_ch1_fitpara.json'
                                 incident_energy=eng, )
