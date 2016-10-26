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

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/2013_sorted/scan1512/'
#sample1_df = '33dfad67-f6eb-4652-8b6c'
#sample1_wf1 = '4c0fe778-5c37-41cd-8599'
#sample1_proj = '622ed471-c0ad-4e88-84a7'	
#sample1_wf2 = '7054b332-1cad-44d4-9ca8'
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1512'

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1267/'
#sample1_df = '1ba2d6ca-28cf-459c-95a8'   #one scan prior to df
#sample1_wf1 = '707312d4-88d8-40d3-8d2d'  #one scan prior to proj in the log
#sample1_proj = 'ba4daae2-1568-41bc-b35c' #scan corresponds to scanid	
#sample1_wf2 = 'da0bf3fc-651d-4bcd-8a30'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1267'
##sample1_center = 434

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1279/'
#sample1_df = '442d4af8-5ea5-435b-9125'   #one scan prior to df
#sample1_wf1 = 'e5d29bcd-4e3d-4252-9a0d'  #one scan prior to proj in the log
#sample1_proj = '01c3f5ef-b960-4e1b-96cc' #scan corresponds to scanid	
#sample1_wf2 = 'ce52547f-d449-4fa3-ac11'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1279'
##sample1_center = 390


#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1291/'
#sample1_df = '1acbc008-5792-4e15-a2b7'   #one scan prior to df
#sample1_wf1 = '03459b06-e285-44d0-a629'  #one scan prior to proj in the log
#sample1_proj = 'f790e06b-d1f0-436c-935f' #scan corresponds to scanid	
#sample1_wf2 = '11ad5333-e045-4b77-93be'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1291'
##sample1_center = 393
##sample1_center = 387 #test_twice

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1303/'
#sample1_df = 'a7ea46ae-98ad-4178-a5ee'   #one scan prior to df
#sample1_wf1 = '67273127-5afd-4c20-af77'  #one scan prior to proj in the log
#sample1_proj = '42a21723-9747-46c7-a208' #scan corresponds to scanid	
#sample1_wf2 = '22c7fbd3-2f4c-4923-8944'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1303'
##sample1_center = 393

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1315/'
#sample1_df = '8b6aa0d7-628b-4df6-aeea'   #one scan prior to df
#sample1_wf1 = 'ebad656c-a72c-4593-974a'  #one scan prior to proj in the log
#sample1_proj = 'ccb2acbb-0f33-4aef-aafa' #scan corresponds to scanid	
#sample1_wf2 = 'aa80fef1-4a63-499f-9473'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1315'
##sample1_center = CANNOT FIND

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1327/'
#sample1_df = '1ce85c2b-cc0b-44dc-863c'   #one scan prior to df
#sample1_wf1 = '7a920047-b8d0-446f-9f8e'  #one scan prior to proj in the log
#sample1_proj = '47c9b62c-743c-46f2-82a8' #scan corresponds to scanid	
#sample1_wf2 = '959900ba-b2a1-4d53-b5d2'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1327'
##sample1_center = 394

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1339/'
#sample1_df = '4e8983f4-9e94-4151-8ee1'   #one scan prior to df
#sample1_wf1 = '84582f71-b3fc-4618-8d04'  #one scan prior to proj in the log
#sample1_proj = 'b56b96fe-c624-4946-a9ea' #scan corresponds to scanid	
#sample1_wf2 = '0fd1ecff-56b6-465e-94b6'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1339'
##sample1_center = 394 # ERROR- index 1443 is out of bounds for axis 0 with size 1441

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1351/'
#sample1_df = '2f1fda2d-c8fe-4c06-b1fc'   #one scan prior to df
#sample1_wf1 = '8bd864b2-c9fe-4a10-9b34'  #one scan prior to proj in the log
#sample1_proj = 'dca93ebb-072e-476a-85a6' #scan corresponds to scanid	
#sample1_wf2 = 'ce61892c-18a5-4bd9-9035'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1351'
##sample1_center = 393

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1373/'
#sample1_df = '39e83dd4-88e7-41bf-8f9c'   #one scan prior to df
#sample1_wf1 = '24e93e9e-4fa5-4269-bcf6'  #one scan prior to proj in the log
#sample1_proj = '992eabb0-ee36-4cd3-8b6b' #scan corresponds to scanid	
#sample1_wf2 = '99091b1d-22d9-4856-8861'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1373'
##sample1_center = 381  

filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1385/'
sample1_df = '39d39a2d-6eea-4c78-98f8'   #one scan prior to df
sample1_wf1 = 'd761856d-f871-420b-89e3'  #one scan prior to proj in the log
sample1_proj = '794301ca-62ae-4c1e-a350' #scan corresponds to scanid	
sample1_wf2 = 'b7637fb3-1691-4407-9419'  #one scan post proj in the log

out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
sample1_name = 'recon1385'
#sample1_center = 387 # looks extremely simiar to sample 1373 #when run second time, it shows out of index, with one extra frame;first center is 381, second is 387

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1488/'
#sample1_df = '9e7cef56-cd75-49c2-9183'   #one scan prior to df
#sample1_wf1 = '9cb7fd4d-792f-478a-aeec'  #one scan prior to proj in the log
#sample1_proj = '0704ddc1-f9ba-4480-9992' #scan corresponds to scanid	
#sample1_wf2 = '2b909309-2493-4736-acc6'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1488'
##sample1_center = 397

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1500/'
#sample1_df = 'c51770dc-6e6a-4f64-97dd'   #one scan prior to df
#sample1_wf1 = '1c1b9103-6048-400e-b059'  #one scan prior to proj in the log
#sample1_proj = '356119fb-62eb-43bb-8c80' #scan corresponds to scanid	
#sample1_wf2 = 'f9bed656-ae8f-4b38-ad0f'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1500'
##sample1_center = 400

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1512/'
#sample1_df = '33dfad67-f6eb-4652-8b6c'   #one scan prior to df
#sample1_wf1 = '4c0fe778-5c37-41cd-8599'  #one scan prior to proj in the log
#sample1_proj = '622ed471-c0ad-4e88-84a7' #scan corresponds to scanid	
#sample1_wf2 = '7054b332-1cad-44d4-9ca8'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1512'
##sample1_center = 393  # has been done before

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1524/'
#sample1_df = '1899dcda-82e9-4f16-86cb'   #one scan prior to df
#sample1_wf1 = '7692bd72-e3de-4bd5-a24e'  #one scan prior to proj in the log
#sample1_proj = '60af5861-bfa5-439d-aa82' #scan corresponds to scanid	
#sample1_wf2 = 'f35b2193-7285-4ccd-8250'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1524'
##sample1_center = CANNOT FIND # 404-409 

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1364/'
#sample1_df = 'ce61892c-18a5-4bd9-9035'   #one scan prior to df
#sample1_wf1 = '3f3777e0-2351-40cd-9868'  #one scan prior to proj in the log
#sample1_proj = '6d84bdb0-0a35-47b0-a0dc' #scan corresponds to scanid	
#sample1_wf2 = '86794b8c-b77c-4da0-8993'  #one scan post proj in the log
#
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1364' #1364 is white field, we may need to run 1361? the front 1351 loss one post white field scan
##sample1_center = 399


sample1_name = 'BNW62118147'

raw_filepath = '/home/xf05id1/localdata/SimerTomo_2016cycle3/'
out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/' #to be changed

filepath_sc = raw_filepath+sample1_name+'/'

#sample1_name = 'recon1364' #1364 is white field, we may need to run 1361? the front 1351 loss one post white field scan
##sample1_center = 399

#####################################
datapath = filepath_sc
#dfprefix = sample1_df
#wf1prefix = sample1_wf1 
#wf2prefix = sample1_wf2 
#projprefix = sample1_proj

sample1_df_path = 'df/'   #one scan prior to df
sample1_wf1_path = 'wf1/'  #one scan prior to proj in the log
sample1_proj_path = 'proj/' #scan corresponds to scanid	
sample1_wf2_path = 'wf2/'  #one scan post proj in the log
dfprefix = listdir(filepath_sc+sample1_df_path)[0][:-12:]
wf1prefix = listdir(filepath_sc+sample1_wf1_path)[0][:-12:]
wf2prefix = listdir(filepath_sc+sample1_wf2_path)[0][:-12:]
projprefix = listdir(filepath_sc+sample1_proj_path)[0][:-12:]

outpath = out_filepath
samplename = sample1_name
#sample1_center = 393	#test



outputfile_tiff = outpath + samplename + '/' + samplename +'_corrected.tiff'

#suggest work flow:
#%run '/nfs/xf05id1/src/nsls2-xf-utils/srxfftomo_parameters.py'
proj = srxfftomo_process.srxfftomo_correction(filepath_sc, sample1_df, sample1_wf1, sample1_wf2, sample1_proj, outpath = out_filepath, samplename = sample1_name)
srxfftomo_process.srxfftomo_findcenter(proj = proj, autocheck = True, outpath = out_filepath, samplename = sample1_name)
#srxfftomo_process.srxfftomo_findcenter(proj = proj, check_cen_range_step = [390, 410, 1], outpath = out_filepath, samplename = sample1_name)  #find update center
#srxfftomo_process.srxfftomo_recon(proj=proj, rot_center = 434, outpath = out_filepath, samplename = sample1_name)