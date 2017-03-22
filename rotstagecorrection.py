# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 14:06:54 2016

@author: xf05id1
"""

from __future__ import print_function
import tomopy, dxchange
from tifffile import imread
from PIL import Image
import tomopy
import numpy
import scipy.ndimage
import os, sys
import numpy as np
from scipy import ndimage
from scipy.ndimage.interpolation import shift
import matplotlib.pyplot as plt


#dpath = '/home/xf05id1/localdata/TomoCommissioning/pintest_run3_1441proj/img_shift_xonlyseg_cencheck/'


#def gen_tomostage_calib(filepath, sample1_proj, outpath = out_filepath, samplename = sample1_name):
#
#    df_path = 'df/'   #one scan prior to df
#    wf1_path = 'wf1/'  #one scan prior to proj in the log
#    sample1_proj_path = 'proj/' #scan corresponds to scanid	
#    sample1_wf2_path = 'wf2/'  #one scan post proj in the log
#    dfprefix = listdir(filepath_sc+sample1_df_path)[0][:-12:]
#    wf1prefix = listdir(filepath_sc+sample1_wf1_path)[0][:-12:]
#    wf2prefix = listdir(filepath_sc+sample1_wf2_path)[0][:-12:]
#    projprefix = listdir(filepath_sc+sample1_proj_path)[0][:-12:]


def calib(cal_indir, cal_infn, center_check_path = None, use_cal_indir_as_center_check_path = True, hist_threshold = 1.5, max_threshold = 10):

    '''
    max_threshold: larger then this value, set img(x,y) = 0.001 to avoid numerical errors
    '''    
    
    plt.ion()
    #cal_indir = '/nfs/xf05id1/data/beamlineData/fullfield_comissioning/pintest_run1_361proj/'
    #cal_indir = '/home/xf05id1/localdata/TomoCommissioning/pintest_run1_361proj/'
    #cal_infn = 'pintest_run1_361proj_norm.tif'
    #cal_infn = 'pintest_run3_1441proj_norm.tif'

    cal_infile = cal_indir + cal_infn
    img = imread(cal_infile)
    img = (-1)*np.log(img)

    #
    #plt.figure()
    #plt.plot(cen[:,1])
    
    sino  = img [:, 400, :]
    #plt.plot(range(sino.shape[1]), sino[0, :])
    plt.figure()
    plt.imshow(sino)
    plt.show()   
    
    img = tomopy.misc.corr.remove_nan(img, val=0.001)
    img[img > max_threshold] = 0.001
    
    #plot histogram
    hist, bin_edges = np.histogram(img, bins=120, range = (-2.0, 4.0))
    bin_centers = 0.5*(bin_edges[:-1] + bin_edges[1:])    
    plt.figure()
    plt.plot(bin_centers, hist)
      
    #segment the image by threshold = hist_threshold
    binary_img = img > hist_threshold
    plt.figure()
    plt.imshow(img[0, :, :])
    plt.figure()
    plt.imshow(binary_img[0,:,:])


    cen = np.array([ndimage.measurements.center_of_mass(binary_img[i,:, :]) for i in range(binary_img.shape[0])])


    if use_cal_indir_as_center_check_path is True:
        center_check_path = cal_indir

    if center_check_path is not None:
        print('shifting images....')
        img_shift_xonlyseg = np.array([shift(img[i, :, :], [0, cen[:,1].mean()-cen[i,1]]) for i in range(img.shape[0])])
        sino_shift_xonlyseg = img_shift_xonlyseg[:, 400, :]
        plt.figure()
        plt.imshow(sino_shift_xonlyseg)
        plt.show()
        
        theta = tomopy.angles(binary_img.shape[0])
        tomopy.write_center(img_shift_xonlyseg, theta, 
                            center_check_path, cen_range = [390, 410, 1], ind = 400, mask = True)
    
    f=open('cen_seg_x.txt', 'w')
    for i in cen:
        f.write(str(i[1])+'\n')
    f.close()

    return img, cen, img_shift_xonlyseg

