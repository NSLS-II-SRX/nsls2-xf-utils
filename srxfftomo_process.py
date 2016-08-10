# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 10:33:12 2016

@author: xf05id1
this program should
1. load data
2. dark field subtraction, normalize background
3. apply calibration file for shift
4. reconstruct image
"""

import tifffile
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.ndimage.interpolation import shift
import tomopy
import scipy.ndimage
import skimage.measure

def srxfftomo_fileio(datapath, prefix, return_avg = True,
                     print_infile = False):
    '''
    load frames from datapath with prefix
    if return_avg is True, only the average will be returned (useful for dark field and white field)
    otherwise all frames will be returned
    '''
    
    frames = []
    for i in os.listdir(datapath):
        if os.path.isfile(os.path.join(datapath,i)) and prefix in i:
            infile = os.path.join(datapath,i)
            if print_infile is True:
                print(infile)
            frame = tifffile.imread(infile)
            frames.append(frame)
    frames = np.array(frames)

    if return_avg is True:
        frames = np.average(frames, axis = 0)

    return frames
    
def srxfftomo_fileio_proj(datapath, prefix, imgsize = None, numframes = 1441,
                          print_infile = False, print_fcounter = False):
    '''
    load frames from datapath with prefix in order
    '''    
    fcounter = 1
    frames = np.zeros([numframes, imgsize[0], imgsize[1]])
    for i in os.listdir(datapath):
        if os.path.isfile(os.path.join(datapath,i)) and prefix in i:
            infile = os.path.join(datapath,i)
            if print_fcounter is True:            
                print('loading file number:', fcounter)

            if print_infile is True:
                print(infile)
            num = int(i[-9:-5])
            #print(num)
            frames[num, :, :] = tifffile.imread(infile)
            fcounter = fcounter + 1
            
    frames = np.array(frames)
    print('    loaded total projection frames: ', fcounter-1)

    return frames

def srxfftomo_getdata(datapath, dfprefix, wf1prefix, wf2prefix, projprefix, 
                       showimg = True):

    print('    loading dark field images')
    df = srxfftomo_fileio(datapath, dfprefix, return_avg = True)

    print('    loading white field images')
    wf=[]    
    wf1 = srxfftomo_fileio(datapath, wf1prefix, return_avg = True)
    wf2 = srxfftomo_fileio(datapath, wf2prefix, return_avg = True)
    wf.append(wf1)
    wf.append(wf2)
    wf = np.average(wf, axis=0)
    
    print('    loading projection images')
    proj = srxfftomo_fileio_proj(datapath, projprefix, imgsize = wf.shape, numframes = 1441)
  
    if showimg is True:
        plt.close('all')           
        plt.ion()
        plt.figure()
        plt.imshow(df)
        plt.figure()
        plt.imshow(wf1)
        plt.figure()
        plt.imshow(wf2)
        plt.figure()  
        plt.imshow(wf)
        plt.figure()  
        plt.imshow(proj[0, :, :])             
       
    return df, wf, proj
       
def srxfftomo_bkg_correction(df, wf, proj):

    print('    dark field correction')
    wf = wf-df
    proj = proj-df
    
    print('    white field normalization')    
    proj = proj/wf
    
    return proj
    
def srxfftomo_data_reduction(proj, datatype_set = 'float32', 
                             downsample_factor = 1, downsample_order = 2, downsample_func = 'skimage'):
                                 
    '''
    downsample_func = 'skimage': skimage.measure.block_reduce  
    downsample_func = 'scipy':  scipy.ndimage.zoom      
    
    '''
    
    if downsample_factor is not 1:
        print('    down sampling data in (x, y) by ', downsample_factor)
        print('    with order ', downsample_order)

        if downsample_func is 'skimage':
            proj = skimage.measure.block_reduce(proj, (1, downsample_factor, downsample_factor))

        elif downsample_func is 'scipy':
            proj = scipy.ndimage.zoom(proj, [1, 1./downsample_factor, 1./downsample_factor], order = downsample_order)

    if datatype_set is 'float32':
        print('    converting data to float 32 bits')
        proj = np.float32(proj)
    else:
        print('    no data converstion is done')

    return proj

def srxfftomo_stage_correction(proj):
    '''
    input: projections with background corrected (dark field substrated, white field normalized)
    return: projections corrected with the stage round-out/wobbling
    '''
    cen_seg_x_file = '/home/xf05id1/localdata/TomoCommissioning/pintest_run3_1441proj/cen_seg_x.txt'
    with open(cen_seg_x_file) as f:
        cen_seg_x = [float(x.strip('\n')) for x in f.readlines()]    
    cen_seg_x = np.array(cen_seg_x)

    print('    shifting images')
    proj = np.array([shift(proj[i, :, :], [0, cen_seg_x.mean()-cen_seg_x[i]]) for i in range(proj.shape[0])])
    
    return proj 
    
def srxfftomo_correction(datapath, dfprefix, wf1prefix, wf2prefix, projprefix,
                    save_corrected_tiff = True,
                    save_find_center = True,
                    outpath = None,
                    samplename = None,
                    output_tiff_prefix = '',
                    reduce_data = True,
                    datareduction_datatype = 'float32',
                    datareduction_downsample_factor = 1,
                    datareduction_downsample_order = None,                    
                    correct_stage = True,
                    take_neg_log = True):
                        
    print('getting data')                    
    df, wf, proj = srxfftomo_getdata(datapath, dfprefix, wf1prefix, wf2prefix, projprefix, 
                       showimg = False)
                       
    print('correcting background')
    proj = srxfftomo_bkg_correction(df, wf, proj)
    
    if reduce_data is True:
        print('reducing data')
        proj = srxfftomo_data_reduction(proj, datatype_set = datareduction_datatype, 
                             downsample_factor = datareduction_downsample_factor, downsample_order = datareduction_downsample_order)
        output_tiff_prefix = '_resam_' + str(datareduction_downsample_factor) + '_dtypef32'
                             
    if correct_stage is True:
        print('correcting stage round out')    
        proj = srxfftomo_stage_correction(proj)   
        output_tiff_prefix = output_tiff_prefix + '_stgcorr'

    if take_neg_log is True:
        print('taking negative natural log')
        proj = tomopy.minus_log(proj)
        
        print('    handling special values: negatives, Nan, infinite')
        proj = tomopy.misc.corr.remove_neg(proj, val=0.001)
        proj = tomopy.misc.corr.remove_nan(proj, val=0.001)
        proj[np.where(proj == np.inf)] = 0.001
        output_tiff_prefix = output_tiff_prefix + '_neglog'

    if save_corrected_tiff is True:
        outputfile_tiff = outpath + samplename + '/' + samplename + output_tiff_prefix + '.tiff'
        print('saving corrected data into: ' + outputfile_tiff)
        outdir = os.path.dirname(outputfile_tiff)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        tifffile.imsave(outputfile_tiff, proj)
    
    return proj

#################

def srxfftomo_findcenter(corrected_proj_tiff = None, proj = None, 
                            save_find_center = True, autocheck = False,
                            check_cen_range_step = [390, 410, 1], 
                            auto_selecslice = True, cen_slice = 400,
                            outpath = None, samplename = None):

    '''
    input needs to be either 
    1) corrected_proj_tiff, provided as a file path and name, 
    e.g. '/home/xf05id1/localdata/TomoCommissioning/testsample_01/testsample_01_corrected.tiff'
    it is a stack of tiff generated by srxfftomo_correction, where background and stage round out have been corrected
    2) projection numpy array, returned from srxfftomo_correction
    
    The 'proj' array assignment has priority. If it is None, proj was be read from corrected_proj_tiff 
    
    input example:
        check_cen_range_step = [390, 410, 1]
        cen_slice = 400    
    
    return: 
    proj (numpy array, float), with negative natural log has been taken
    
    '''    
    if proj is None:
        print('proj is not asigned, load corrected projection from:', corrected_proj_tiff)
        proj = tifffile.imread(corrected_proj_tiff)
    else:
        print('proj array is not None, use it as is')
    
    if save_find_center is True:
        center_check_path = outpath +'/' + samplename + '/center_check/'
        print('saving find center value into ' +  center_check_path)   

        theta = tomopy.angles(proj.shape[0])
        
        if autocheck is True:
            check_cen_range_step = [int(proj.shape[2]/2)-50, int(proj.shape[2])/2+50, 5]

        if auto_selecslice is True:        
            cen_slice = int(proj.shape[1]/2)
        
        tomopy.write_center(proj, theta, 
                            center_check_path, cen_range = check_cen_range_step, ind = cen_slice, mask = True)
    
    return proj
#               
                                        
def srxfftomo_recon(corrected_proj_tiff = None, proj = None, 
                    rot_center = None, recon_algorithm = 'art', recon_section = None,
                    outpath = None, recon_outpath = 'recon', samplename = None):

    '''
    input needs to be either 
    1) corrected_proj_tiff, provided as a file path and name, 
    e.g. '/home/xf05id1/localdata/TomoCommissioning/testsample_01/testsample_01_corrected.tiff'
    it is a stack of tiff generated by srxfftomo_correction, where background and stage round out have been corrected
    2) projection numpy array, returned from srxfftomo_correction
    
    The 'proj' array assignment has priority. If it is None, proj was be read from corrected_proj_tiff 
    
    recon_section is a list of upper and lower bounds for y range, e.g. [380, 420]
    
    '''
    
    if proj is None:
        print('proj is not asigned, load corrected projection from:', corrected_proj_tiff)
        proj = tifffile.imread(corrected_proj_tiff)
    else:
        print('proj array is not None, use it as is')

    print('running reconstruction')

    if recon_section is not None:    
        proj = proj [:, recon_section[0]:recon_section[1], :]
    
    theta = tomopy.angles(proj.shape[0])
    rec = tomopy.recon(proj, theta, center=rot_center, algorithm= recon_algorithm)

    print('saving reconstruction into')
    recon_outfile = outpath +'/' + samplename + '/' + recon_outpath +'/' + samplename + '_recon'
    tomopy.write_tiff_stack(rec, fname=recon_outfile)
    
    return rec