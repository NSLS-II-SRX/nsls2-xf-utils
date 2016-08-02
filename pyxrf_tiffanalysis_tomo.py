# -*- coding: utf-8 -*-
"""
Created on Thu May 19 12:10:35 2016

@author: xf05id1
"""

from PIL import Image
import matplotlib.pylab as plt
import numpy
import scipy.ndimage
import os, sys
import numpy as np
from tifffile import imsave
#in ipython:
#In [28]: %run /nfs/xf05id1/src/nsls2-xf-utils/pyxrf_tiffanalysis_tomo.py
#In [29]: tiff_batch_process_tomo(wd, scan_list, samplename)


CuS_tomo_wd = '/nfs/xf05id1/userdata/2016_cycle2/300441_Thieme-tomography_comissioning/20160624_CuS_xrftomo/' 
CuS_scanlist = [542, 605, 545, 608, 548,
                611, 551, 614, 554, 617,
                557, 620, 560, 623, 563,
                626, 566, 629, 569, 632, 
                572, 635, 575, 638, 578, 
                641, 581, 644, 584, 647, 
                587, 650, 590, 653, 593, 
                656, 596]

CuS_scanlist = [542, 605, 545, 608, 548,
                611, 551, 614, 554, 617,
                557, 620, 560, 662, 563,
                626, 566, 629, 569, 632, 
                572, 635, 575, 638, 578, 
                641, 581, 644, 584, 647, 
                587, 650, 590, 653, 593, 
                656, 596]
                
theta = np.linspace(-90, 90, num = 37)
    
#CuS_scanlist = [542]            


wd = CuS_tomo_wd
scan_list =  CuS_scanlist
samplename = 'CuStomo' 
maxscale = 2.00e13
minscale = 0.15e13


def tiff_batch_process_tomo(wd, scan_list, samplename, noscale = False, h5prefix = 'CuS_xrftomo',
                       shownormonly = True, closefigwhendone = True, save_normfig = False, element = 'Fe_K',
                       combine_tiff = True, output_combine_tiff = True, combinetiff_outfn = 'notalign',
                       resampling_factor = 1, outfile_noscanid = False,
                       fixydim = True, ydim = 41, imgshape=(41, 41),
                       maxscale = maxscale, minscale = minscale):

    if combine_tiff is True:
        tomodata = numpy.zeros((len(theta), imgshape[0], imgshape[1]), 'float32')
    else:
        tomodata = None
    
    plt.ion()
    
    if noscale is False:
        fnaddon = '_scale'
    else:
        fnaddon = '_autoscale'
        
    if resampling_factor is not 1:
        fnaddon = fnaddon + '_resam' + str(resampling_factor)
    
    if noscale is True:
        minscale = None
        maxscale = None
    
    plt.close("all")
    
    if save_normfig:
        fig_norm_folder = wd + samplename + '_norm' + fnaddon + '/'
        try:    
            os.makedirs(fig_norm_folder)
        except Exception as e:
            print(e)
            print('cannot create directory:' + fig_norm_folder)
            sys.exit()
    
    
    for idx, scanid in enumerate(scan_list):
        plt.figure()
        print('angle number', idx)
        print('scanid', scanid)
    
        scanfolder = wd + 'output_tiff_' + h5prefix + str(scanid)+'/'
        scan_data = scanfolder+'detsum_'+element+'.tiff'
        scan_I0 = scanfolder+'current_preamp_ch2.tiff'
        
        if outfile_noscanid:
            fig_norm_file = '{:03d}'.format(idx) + 'norm' + fnaddon + '.png'
        else:
            fig_norm_file = '{:03d}'.format(idx) + '_' + str(scanid) + 'norm' + fnaddon + '.png'            
    
        im1 = Image.open(scan_data)
        im2 = Image.open(scan_I0)
        
        if shownormonly is not True:
            plt.figure()
            implot = plt.imshow(numpy.array(im1), vmin = minscale, vmax = maxscale, interpolation = 'none')
            plt.colorbar()
            
            plt.figure()
            implot = plt.imshow(numpy.array(im2), vmin = minscale, vmax = maxscale, interpolation = 'none')
            plt.colorbar()
        
        #plt.figure()
        norm_img = numpy.array(im1)/numpy.array(im2)
        print('original image shape', norm_img.shape)
        norm_img = scipy.ndimage.zoom(norm_img, resampling_factor, order=3)
        print('resampled image shape', norm_img.shape)
        
        if fixydim is True:
            if norm_img.shape[0] is not ydim:
                tmp = norm_img
                norm_img = numpy.zeros(imgshape)
                norm_img[0:-1][:] = tmp
                print('fixed image', norm_img.shape)
                       
        implot = plt.imshow(norm_img, vmin = minscale, vmax = maxscale, interpolation = 'none')
        plt.colorbar()
    
        if save_normfig is True:    
            plt.savefig(fig_norm_folder + fig_norm_file)
        if closefigwhendone:
            plt.close('all')
        if combine_tiff is True:
            tomodata[idx][:][:] = norm_img
        if output_combine_tiff is True:
            imsave(wd+element+combinetiff_outfn+'.tif', tomodata)   
            
            
    return tomodata


    #plt.show()

    

 