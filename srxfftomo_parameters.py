# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 10:22:29 2016

@author: xf05id1
"""
#note: 1351 missing post scan wf

import matplotlib.pyplot as plt
import numpy as np
from imp import reload
import srxfftomo_process

plt.ion()

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/sample_0/'
#sample1_df = '1ba2d6ca-28cf-459c-95a8'
#sample1_wf1 = '707312d4-88d8-40d3-8d2d'
#sample1_proj = 'ba4daae2-1568-41bc-b35c'	
#sample1_wf2 = 'da0bf3fc-651d-4bcd-8a30'
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/'
#sample1_name = 'testsample_03'

filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/2013_sorted/scan1512/'
sample1_df = '33dfad67-f6eb-4652-8b6c'
sample1_wf1 = '4c0fe778-5c37-41cd-8599'
sample1_proj = '622ed471-c0ad-4e88-84a7'	
sample1_wf2 = '7054b332-1cad-44d4-9ca8'

out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
sample1_name = 'recon1512'


#####################################
datapath = filepath_sc
dfprefix = sample1_df
wf1prefix = sample1_wf1 
wf2prefix = sample1_wf2 
projprefix = sample1_proj

outpath = out_filepath
samplename = sample1_name
#sample1_center = 436	#test
sample1_center = 404


outputfile_tiff = outpath + samplename + '/' + samplename +'_corrected.tiff'

#suggest work flow:
#%run '/nfs/xf05id1/src/nsls2-xf-utils/srxfftomo_parameters.py'
#proj = srxfftomo_process.srxfftomo_correction(filepath_sc, sample1_df, sample1_wf1, sample1_wf2, sample1_proj, outpath = out_filepath, samplename = sample1_name)
#srxfftomo_process.srxfftomo_findcenter(proj = proj, autocheck = True, outpath = out_filepath, samplename = sample1_name)
#srxfftomo_process.srxfftomo_findcenter(proj = proj, check_cen_range_step = [390, 410, 1], outpath = out_filepath, samplename = sample1_name)  #find update center
#srxfftomo_process.srxfftomo_recon(proj=proj, rot_center = 436, outpath = out_filepath, samplename = sample1_name)