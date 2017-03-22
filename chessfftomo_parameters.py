#note: 1351 missing post scan wf



import matplotlib.pyplot as plt
import numpy as np
from imp import reload
import srxfftomo_process



plt.ion()

#filepath_sc = '/home/xf05id1/localdata/TomoCommissioning/Ecker_raw_sorted/scan1385/'

chess_datapath = '/home/xf05id1/localdata/CHESSdata/NFA1300_11_nf/nf/'

sample1_name = '2048-590all.tif'


#sample1_df = '39d39a2d-6eea-4c78-98f8'   #one scan prior to df
#sample1_wf1 = 'd761856d-f871-420b-89e3'  #one scan prior to proj in the log
#sample1_proj = '794301ca-62ae-4c1e-a350' #scan corresponds to scanid	
#sample1_wf2 = 'b7637fb3-1691-4407-9419'  #one scan post proj in the log

#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/'
#sample1_name = 'recon1385'

#sample1_center = 387 # looks extremely simiar to sample 1373 #when run second time, it shows out of index, with one extra frame;first center is 381, second is 387



#sample1_name = 'BNW62118147'
#
#
#
#raw_filepath = '/home/xf05id1/localdata/SimerTomo_2016cycle3/'
#out_filepath = '/home/xf05id1/localdata/TomoCommissioning/sorted_recon/' #to be changed


filepath_sc = raw_filepath+sample1_name+'/'



#sample1_name = 'recon1364' #1364 is white field, we may need to run 1361? the front 1351 loss one post white field scan
##sample1_center = 399



#####################################

datapath = filepath_sc

#dfprefix = sample1_df
#wf1prefix = sample1_wf1 
#wf2prefix = sample1_wf2 
#projprefix = sample1_proj



#sample1_df_path = 'df/'   #one scan prior to df
#sample1_wf1_path = 'wf1/'  #one scan prior to proj in the log
#sample1_proj_path = 'proj/' #scan corresponds to scanid	
#sample1_wf2_path = 'wf2/'  #one scan post proj in the log
#dfprefix = listdir(filepath_sc+sample1_df_path)[0][:-12:]
#wf1prefix = listdir(filepath_sc+sample1_wf1_path)[0][:-12:]
#wf2prefix = listdir(filepath_sc+sample1_wf2_path)[0][:-12:]
#projprefix = listdir(filepath_sc+sample1_proj_path)[0][:-12:]




#outpath = out_filepath
#
#samplename = sample1_name

#sample1_center = 393	#test



outputfile_tiff = outpath + samplename + '/' + samplename +'_corrected.tiff'



#suggest work flow:

#%run '/nfs/xf05id1/src/nsls2-xf-utils/srxfftomo_parameters.py'
#proj = srxfftomo_process.srxfftomo_correction(filepath_sc, sample1_df, sample1_wf1, sample1_wf2, sample1_proj, outpath = out_filepath, samplename = sample1_name)
#srxfftomo_process.srxfftomo_findcenter(proj = proj, autocheck = True, outpath = out_filepath, samplename = sample1_name)
##srxfftomo_process.srxfftomo_findcenter(proj = proj, check_cen_range_step = [390, 410, 1], outpath = out_filepath, samplename = sample1_name)  #find update center
##srxfftomo_process.srxfftomo_recon(proj=proj, rot_center = 434, outpath = out_filepath, samplename = sample1_name)

#%run '/nfs/xf05id1/src/nsls2-xf-utils/srxfftomo_parameters.py'
proj = srxfftomo_process.chess_proj(chess_datapath, fname = sample1_name, imgsize = [664, 590])
srxfftomo_process.srxfftomo_findcenter(proj = proj, autocheck = True, cen_slice = 315, outpath = chess_datapath, samplename = sample1_name)
#srxfftomo_process.srxfftomo_findcenter(proj = proj, check_cen_range_step = [390, 410, 1], outpath = chess_datapath, samplename = sample1_name)  #find update center
#srxfftomo_process.srxfftomo_recon(proj=proj, rot_center = 434, outpath = out_filepath, samplename = sample1_name)
