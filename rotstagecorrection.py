# -*- coding: utf-8 -*-
"""
Created on Mon Jul 11 14:06:54 2016

@author: xf05id1
"""

from __future__ import print_function
import tomopy, dxchange
from tifffile import imread
from PIL import Image

import numpy
import scipy.ndimage
import os, sys
import numpy as np
from scipy import ndimage
from scipy.ndimage.interpolation import shift
import matplotlib.pyplot as plt


dpath = '/home/xf05id1/localdata/TomoCommissioning/pintest_run3_1441proj/img_shift_xonlyseg_cencheck/'

def calib(cal_indir, cal_infn, center_check_path = None, hist_threshold = 1.5):
    
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

    #plot histogram
    hist, bin_edges = np.histogram(img, bins=60)
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
    
    return img, cen    

