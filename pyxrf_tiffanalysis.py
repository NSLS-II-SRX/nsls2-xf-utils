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
import tifffile
#import scipy.misc

import matplotlib.animation as animation
from pylab import *

#in ipython:
#In [28]: %run /nfs/xf05id1/src/nsls2-xf-utils/pyxrf_tiffanalysis.py
#In [29]: tiff_batch_process(wd, scan_list, samplename)


##
cell01_cathode_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell01_cathode/'
cell01_cathode = [2669, 2681, 2685, 2689, 2693, 2697, 2701, 2705, 2709, 2713, 2717]
#cell01_cathode = [2669] #for testing    
#
#cell01_cathode    
maxscale = 1.6e13
minscale = 0.2e13
#axis_xlim = [-20, 75000]
axis_xlim = None

wd = cell01_cathode_wd
scan_list =  cell01_cathode
samplename = 'cell01_cathode' 
timestamp_file = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/cell01_cathode.txt'

#
#cell01_anode_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell01_anode/'    
#cell01_anode = [2679, 2682, 2686, 2690, 2694, 2698, 2702, 2706, 2710, 2714, 2718]
#
#maxscale = 6.0e12
#minscale = 0.4e12
#axis_xlim = None
#
#wd = cell01_anode_wd
#scan_list =  cell01_anode
##scan_list = [2679, 2686] #for test
#samplename = 'cell01_anode' 
#timestamp_file = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/cell01_anode.txt'

#ec_voltage_fn = 'cell01_Ewe_V.txt'
#ec_capacity_fn = 'cell01_capacity_mAhg-1.txt'
#ec_time_fn = 'cell01_time_s.txt'

cell04_cathode_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell04_cathode/' 
#cell04_cathode = [2725, 2730, 2734, 2739, 2743, 2747, 2751, 2755, 2759, 2763, 2767, 2771, 2775, 2779]
#axis_xlim = [-20, 80000]
axis_xlim = None
cell04_cathode = [2755, 2771]

maxscale = 1.6e13
minscale = 0.2e13

wd = cell04_cathode_wd
scan_list =  cell04_cathode
samplename = 'cell04_cathode' 
timestamp_file = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/cell04_cathode.txt'
###
#cell04_anode_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell04_anode/' 
#cell04_anode = [2727, 2731, 2735, 2740, 2744, 2748, 2752, 2756, 2760, 2764, 2768, 2772, 2776, 2780]
##cell04_anode = [2727] #testing
##maxscale = 6.0e12
##minscale = 0.4e12
##
#wd = cell04_anode_wd
#scan_list =  cell04_anode
#samplename = 'cell04_anode' 
#timestamp_file = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/cell04_anode.txt'
#maxscale = 4.4e12
#minscale = 0.4e12
#axis_xlim = [-20, 75000]
#
#ec_voltage_fn = 'cell04_Ewe_V.txt'
#ec_capacity_fn = 'cell04_capacity_mAhg-1.txt'
#ec_time_fn = 'cell04_time_s.txt'
#
ec_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/ElectrochemicalData/'



def ecdata_input(ec_wd = ec_wd, 
                 ec_voltage_file = ec_voltage_fn, 
                 ec_capacity_file = ec_capacity_fn,
                 ec_time_file = ec_time_fn, 
                 showplot = False):

    plt.ion()
    with open(ec_wd+ec_voltage_file) as f:
        ec_voltage = [float(x.strip('\n').strip('\r')) for x in f.readlines()]
    ec_voltage = numpy.array(ec_voltage)
    
    with open(ec_wd+ec_capacity_file) as f:
        ec_capacity = [float(x.strip('\n').strip('\r')) for x in f.readlines()]
    ec_capacity = numpy.array(ec_capacity)

    with open(ec_wd+ec_time_file) as f:
        ec_time = [float(x.strip('\n').strip('\r')) for x in f.readlines()]
    ec_time = numpy.array(ec_time)

    if showplot is True:
        plt.figure()
        plt.plot(ec_capacity, ec_voltage)    
        plt.show()
    
    return ec_capacity, ec_voltage, ec_time


def tiff_batch_process(wd, scan_list, samplename, noscale = False, 
                       shownormonly = True, closefigwhendone = True, save_normfig = True,
                       resampling_factor = 2, close_all_fig = True,
                       maxscale = maxscale, minscale = minscale):
    
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
    
    if close_all_fig:
        plt.close("all")
    
    if save_normfig is True:
        fig_norm_folder = wd + samplename + '_norm' + fnaddon + '/'
        try:    
            os.makedirs(fig_norm_folder)
        except Exception as e:
            print(e)
            print('cannot create directory:' + fig_norm_folder)
            sys.exit()
    
    for scanid in scan_list:
    
        scanfolder = wd + 'output_tiff_' + str(scanid)+'/'
        scan_Cu = scanfolder+'detsum_Cu_K.tiff'
        scan_I0 = scanfolder+'current_preamp_ch2.tiff'
        
        fig_norm_file = str(scanid) + 'norm' + fnaddon + '.png'
        
        im1 = Image.open(scan_Cu)
        im2 = Image.open(scan_I0)
        
        if shownormonly is not True:
            plt.figure()
            implot = plt.imshow(numpy.array(im1), vmin = minscale, vmax = maxscale, interpolation = 'none')
            plt.colorbar()
            
            plt.figure()
            implot = plt.imshow(numpy.array(im2), vmin = minscale, vmax = maxscale, interpolation = 'none')
            plt.colorbar()
        
        plt.figure()
        norm_img = numpy.array(im1)/numpy.array(im2)
        print(norm_img.shape)
        norm_img = scipy.ndimage.zoom(norm_img, resampling_factor, order=3)
        print(norm_img.shape)
        implot = plt.imshow(norm_img, vmin = minscale, vmax = maxscale, interpolation = 'none')
        plt.colorbar()
    
        if save_normfig is True:    
            plt.savefig(fig_norm_folder + fig_norm_file)        
    
    plt.show()
    if closefigwhendone:
        plt.close('all')
    
    return norm_img


def scan_timestamp(timestamp_file):

    timestamp_dic = {}
    with open(timestamp_file, 'r') as f:
        f.readline()    
        for line in f:
            contents = line.split('\t')
            timestamp_dic[contents[0]] = float(contents[1])        
    return timestamp_dic

    
def tiff_normimg(wd, scanid, ele = 'Cu_K'):
    
    plt.ion()
       
    scanfolder = wd + 'output_tiff_' + str(scanid)+'/'
    scan_ele = scanfolder+'detsum_'+ ele + '.tiff'
    scan_I0 = scanfolder+'current_preamp_ch2.tiff'
        
    im1 = Image.open(scan_ele)
    im2 = Image.open(scan_I0)
        
    norm_img = numpy.array(im1)/numpy.array(im2)
    
    return norm_img


def tiff_ec_coplot(xrfwd = wd, scanidlist = scan_list, timestamp_file = timestamp_file,
                   resampling_factor = 2,savefig = True, save_normtiff = True, 
                   ec_wd = ec_wd, check_xsize = 40, check_ysize = 40,
                   ec_voltage_file = ec_voltage_fn, 
                   ec_capacity_file = ec_capacity_fn,
                   ec_time_file = ec_time_fn):

    plt.ion()                       
    c, v, t = ecdata_input(ec_wd = ec_wd, 
                                              ec_voltage_file = ec_voltage_fn, 
                                              ec_capacity_file = ec_capacity_fn,
                                              ec_time_file = ec_time_fn)
    
    timestamp_dic = scan_timestamp(timestamp_file)
    
    plt.close('all')
    for scanid in scanidlist: 
        f, axrr = plt.subplots(2, gridspec_kw = {'height_ratios':[2.5, 1], 'width_ratios': [1,1]})
        norm_img = tiff_normimg(xrfwd, scanid)
        imgshape = norm_img.shape
        print(imgshape)
        if imgshape[0] is not check_ysize:
            tmp = norm_img
            norm_img = numpy.zeros((check_ysize, check_xsize))
            norm_img[0:(check_ysize-1), 0:check_xsize] = tmp
            norm_img = np.float32(norm_img)
            print(scanid)
        
        norm_img = scipy.ndimage.zoom(norm_img, resampling_factor, order=3)
        im = axrr[0].imshow(norm_img,interpolation='none', vmin = minscale, vmax = maxscale)
        #axrr[0].set_title(samplename)        
        
        axrr[1].plot(t,v)
        axrr[1].axvline(timestamp_dic[str(scanid)]-timestamp_dic[str(scanidlist[0])], linewidth = 3, color='r')
        axrr[1].set_xlabel('time (s)')
        axrr[1].set_ylabel('voltage (V)')
        axrr[1].set_xlim(axis_xlim)
        
        plt.colorbar(im, ax = axrr[0])
        plt.tight_layout()
        plt.subplots_adjust(right=1.55)
        
        axrr[0].axes.get_xaxis().set_visible(False)
        axrr[0].axes.get_yaxis().set_visible(False)

        plt.show()
        
        if savefig is True:
            outputfile = xrfwd + 'ec_coplot_noaxis/' + samplename+'_resam_' + str(resampling_factor)+ '_scan' + str(scanid)
            outdir = os.path.dirname(outputfile)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            plt.savefig(outputfile, bbox_inches='tight')

        if save_normtiff is True:      
            outputfile_tiff = xrfwd + 'ec_coplot_tiff/' + samplename+'_resam_' + str(resampling_factor)+ '_normCu_scan' + str(scanid)+'.tiff'
            outdir = os.path.dirname(outputfile_tiff)
            if not os.path.exists(outdir):
                os.makedirs(outdir)
            #scipy.misc.imsave(outputfile_tiff, norm_img)
            norm_img_32 = np.float32(norm_img)
            tifffile.imsave(outputfile_tiff, norm_img_32)
            
        #return norm_img
        
    
def ani_scan():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    #ax.get_xaxis().set_visible(False)
    #ax.get_yaxis().set_visible(False)

    norm_img = tiff_normimg(cell04_anode_wd, cell04_anode[0])

    im = ax.imshow(norm_img ,interpolation='none', vmin = minscale, vmax = maxscale)
    #im.set_clim([0,1])
    #fig.set_size_inches([5,5])

    #tight_layout()

    def update_img(n):
        norm_img = tiff_normimg(cell04_anode_wd, cell04_anode[10])
        im.set_data(norm_img)
        return im

    #legend(loc=0)
    ani = animation.FuncAnimation(fig,update_img,300,interval=30)
    writer = animation.writers['ffmpeg'](fps=30)

    ani.save('/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/test.mp4',writer=writer,dpi=100)
    return ani