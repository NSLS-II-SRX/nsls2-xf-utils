# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 10:22:29 2016

@author: xf05id1
"""

import matplotlib.pyplot as plt
import numpy as np
from imp import reload
import srxfftomo_process

plt.ion()

filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/sample_0/'
sample1_df = '1ba2d6ca-28cf-459c-95a8'
sample1_wf1 = '707312d4-88d8-40d3-8d2d'
sample1_proj = 'ba4daae2-1568-41bc-b35c'	
sample1_wf2 = 'da0bf3fc-651d-4bcd-8a30'

out_filepath = '/home/xf05id1/localdata/TomoCommissioning/'
sample1_name = 'testsample_02'


datapath = filepath_sc
dfprefix = sample1_df
wf1prefix = sample1_wf1 
wf2prefix = sample1_wf2 
projprefix = sample1_proj

outpath = out_filepath
samplename = sample1_name
sample1_center = 436	

outputfile_tiff = outpath + samplename + '/' + samplename +'_corrected.tiff'

#suggest work flow:
#%run '/nfs/xf05id1/src/nsls2-xf-utils/srxfftomo_parameters.py'
#proj = srxfftomo_process.srxfftomo_correction()
#proj = srxfftomo_process.srxfftomo_findcenter(proj = proj, autocheck = True)
#proj = srxfftomo_process.srxfftomo_findcenter(proj = proj, check_cen_range_step = [390, 410, 1])  #find update center
#srxfftomo_recon(proj, rot_center = 436)