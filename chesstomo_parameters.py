# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 13:43:35 2016

@author: xf05id1
"""

import srxfftomo_process
import tomopy
import numpy as np
from skimage.restoration import denoise_tv_chambolle

reconpath = '/home/xf05id1/localdata/CHESSdata/reconstruction/'


#datapath = '/home/xf05id1/localdata/CHESSdata/spec1_12_nf/nf/'
#projname = '664-590_all.tif'
#
#samplename = 'spec1_12'

#datapath = '/home/xf05id1/localdata/CHESSdata/spec4_6_nf/nf/'
#projname = '664-590_all.tif'
#
#samplename = 'spec4_6'

#datapath = '/home/xf05id1/localdata/CHESSdata/spec5_5_nf/nf/'
#projname = '664-590_all.tif'
#
#samplename = 'spec5_5'


#datapath = '/home/xf05id1/localdata/CHESSdata/spec22_2_nf/nf/'
#projname = '664-590_all.tif'
#
#samplename = 'spec22_2'

#datapath = '/home/xf05id1/localdata/CHESSdata/NFA1300_11_nf/nf/'
#projname = '2048-590all.tif'
#
#samplename = 'NFA1300_11'

#datapath = '/home/xf05id1/localdata/CHESSdata/NFAISSJ2_5_nf/nf/'
#projname = '664-2048-590-all.tif'
#
#samplename = 'NFAISSJ2_5'

#datapath = '/home/xf05id1/localdata/CHESSdata/SiC1_11_nf/nf/'
#projname = '664-590all.tif'
#
#samplename = 'SiC1_11'

datapath = '/home/xf05id1/localdata/CHESSdata/SS_Cl/nf/'
projname = 'SS_Cl_combine_590-664.tif'

samplename = 'SS_Cl'

wf_file_name = '/home/xf05id1/localdata/CHESSdata/darkfield_whitefield/white_field_test_NFA1300_664-590.tif'

#%run /home/xf05id1/src/nsls2-xf-utils/chesstomo_parameters.py


#################
print('loading data')
proj, df, wf = srxfftomo_process.chess_fileio(datapath, projname, wf_file = wf_file_name)
print (proj.shape, wf.shape)
proj = tomopy.remove_outlier(proj, 400, size=6)
proj = tomopy.remove_outlier(proj, 100, size=6)

wf = np.expand_dims(wf, axis=0) #expand the initial 2D white field image into 3D image

wf = tomopy.remove_outlier(wf, 400, size=6)
wf = tomopy.remove_outlier(wf, 100, size=6)
print('correcting background')
proj = srxfftomo_process.srxfftomo_bkg_correction(df, wf, proj)
print('taking negative natural log')
proj = tomopy.minus_log(proj)

print('    handling special values: negatives, Nan, infinite')
proj = tomopy.misc.corr.remove_neg(proj, val=0.001)
proj = tomopy.misc.corr.remove_nan(proj, val=0.001)
proj[np.where(proj == np.inf)] = 0.001

#print('denoise the data...')
#for i in range(proj.shape[0]):
#    print(i)
#    proj[i, :, :] = denoise_tv_chambolle(proj[i, :, :], weight=0.2)

srxfftomo_process.srxfftomo_findcenter(proj = proj, 
                            save_find_center = True, autocheck = True,
                            auto_selecslice = True, outpath = datapath[:-3], samplename = 'center_check', 
                            starting_angle = 0, last_angle = 360)    
                            
#center for sample NFA1300_11 is 1077 #some ring artifact exist
#center for sample NFA1ISSJ2_5 is 1086 #some ring artifact exist
#center for sample SiC1_11 is 1074 #some ring artifact exist, no feature was found
#center for sample spec1_12 is 1077 #some ring artifact exist
#center for sample spec4_6 is 1083 #some ring artifact exist
#center for sample spec5_5 is 1087 #some ring artifact exist
#center for sample spec22_2 is 1087 #some ring artifact exist
#center for sample SS-CL is 1089 #some ring artifact exist

#srxfftomo_process.srxfftomo_findcenter(proj = proj, save_find_center = True, autocheck = False, auto_selecslice = True, outpath = datapath[:-3], samplename = 'center_check', check_cen_range_step = [1077, 1078, 1], starting_angle = 0, last_angle = 360)  
srxfftomo_process.srxfftomo_recon(proj=proj, rot_center = 1089, outpath = reconpath, samplename = samplename, starting_angle = 0, last_angle = 360, recon_algorithm = 'gridrec')

##option: one can specify to only reconstruct few slices, e.g. from slice 300-305 using "recon_section"
#srxfftomo_process.srxfftomo_recon(proj=proj, recon_section = [300, 305], rot_center = 1077, outpath = reconpath, samplename = samplename, starting_angle = 0, last_angle = 360, recon_algorithm = 'gridrec')
