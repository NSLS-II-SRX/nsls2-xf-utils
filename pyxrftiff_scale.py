# -*- coding: utf-8 -*-
"""
Created on Thu May 19 12:10:35 2016

@author: xf05id1
"""

from PIL import Image
import matplotlib.pylab as plt
import numpy

cell01_cathode_pistine_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell01_cathode/2669_output/'
cell01_cathode_discharged_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell01_cathode/2713_output/'
cell01_cathode_pistine = '2669_Cu_norm_scale4x4.tiff'
cell01_cathode_discharged = '2713_Cu_norm_scale4x4.tif'
#cell01_p = '2669_Cu_norm.tiff'

imf_p = cell01_cathode_pistine_wd + cell01_cathode_pistine
imf_d = cell01_cathode_discharged_wd + cell01_cathode_discharged

minscale = 1.6e13
maxscale = 0.2e13

plt.close("all")

plt.figure()
im1 = Image.open(imf_p)
#im.show()
#im = plt.imread(cell01_c_wd+cell01_p)
implot = plt.imshow(numpy.array(im1), vmin = minscale, vmax = maxscale, interpolation = 'none')
plt.colorbar()


plt.figure()
im2 = Image.open(imf_d)
implot = plt.imshow(numpy.array(im2), vmin = minscale, vmax = maxscale, interpolation = 'none')
plt.colorbar()


############
cell01_anode_pistine_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell01_anode/2679_output/'
cell01_anode_discharged_wd = '/nfs/xf05id1/userdata/2016_cycle1/300398_Chen-Wiegart-LiSbattery/batch_xrf_cell01_anode/2718_output/'
cell01_anode_pistine = '2679_Cu_norm_scale4x4.tif'
cell01_anode_discharged = '2718_Cu_norm_scale4x4.tif'

imf_p = cell01_anode_pistine_wd + cell01_anode_pistine
imf_d = cell01_anode_discharged_wd + cell01_anode_discharged

minscale = 0.4e12
maxscale = 7.2e12


plt.figure()
im1 = Image.open(imf_p)
#im.show()
#im = plt.imread(cell01_c_wd+cell01_p)
implot = plt.imshow(numpy.array(im1), vmin = minscale, vmax = maxscale, interpolation = 'none')
plt.colorbar()


plt.figure()
im2 = Image.open(imf_d)
implot = plt.imshow(numpy.array(im2), vmin = minscale, vmax = maxscale, interpolation = 'none')
plt.colorbar()