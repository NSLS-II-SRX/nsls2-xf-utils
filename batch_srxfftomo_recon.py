# -*- coding: utf-8 -*-
"""
Created on Wed Nov  9 19:43:19 2016

@author: xf05id1
"""

import srxfftomo_process
#
#sample_list = ['BNW62118147-3-baggie', 'BNW62118148-3-10poly-CO2-expo', 'BNW62118148-3-10poly-H2SO4-expo', 'BNW62118156', 'clay-10-per-3', 'clay-70-per-1']
#center_list = [443, 482, 458, 456, 477,478]


sample_list = ['clay-70-per-1']
center_list = [478]

#raw_filepath = '/home/xf05id1/localdata/SimerTomo_2016cycle3/'

#filepath_sc = raw_filepath+sample_name+'/'
out_filepath = '/home/xf05id1/localdata/SimerTomo_2016cycle3/reconstruction/'


#sample1_df_path = 'df/'   #one scan prior to df
#sample1_wf1_path = 'wf1/'  #one scan prior to proj in the log
#sample1_proj_path = 'proj/' #scan corresponds to scanid	
#sample1_wf2_path = 'wf2/'  #one scan post proj in the log
#dfprefix = listdir(filepath_sc+sample1_df_path)[0][:-12:]
#wf1prefix = listdir(filepath_sc+sample1_wf1_path)[0][:-12:]
#wf2prefix = listdir(filepath_sc+sample1_wf2_path)[0][:-12:]
#projprefix = listdir(filepath_sc+sample1_proj_path)[0][:-12:]


for index, sample_name in enumerate(sample_list):
    #proj = srxfftomo_process.srxfftomo_correction(filepath_sc, sample1_df_path, sample1_wf1_path, sample1_wf2_path, sample1_proj_path, dfprefix, wf1prefix, wf2prefix, projprefix, outpath = out_filepath, samplename = sample_name)
    #srxfftomo_process.srxfftomo_recon(proj=proj, rot_center = center_list[index], outpath = out_filepath, samplename = sample_name)    

    corrected_proj_tiff_path = out_filepath + sample_name  + '/' + sample_name + '_resam_1_dtypef32_stgcorr_neglog.tiff'
    srxfftomo_process.srxfftomo_recon(corrected_proj_tiff=corrected_proj_tiff_path, rot_center = center_list[index], outpath = out_filepath, samplename = sample_name)    

