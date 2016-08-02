# -*- coding: utf-8 -*-
"""
Created on Wed Jan 27 08:53:10 2016

@author: xf05id1
"""

import srxpeak
from matplotlib import pyplot
import numpy

#test files
#fileprefixList = ['2016_1_27_12_19', #wb 0.8x0.8, ROI3=24x24
#                  '2016_1_27_13_6' #wb 2x2, ROI3=24x24
#                 ]

fileprefixList = [
#HFM Bend 271950.0
'2016_1_29_20_33',
#HFM Bend 269950.0
'2016_1_29_20_36',
#HFM Bend 267950.0
'2016_1_29_20_40',
#HFM Bend 265950.0
'2016_1_29_20_43',
#HFM Bend 263950.0
'2016_1_29_20_47',
#HFM Bend 261950.0
'2016_1_29_20_50',
#HFM Bend 259950.0
'2016_1_29_20_53',
#HFM Bend 257950.0
'2016_1_29_20_56',
#HFM Bend 255950.0
'2016_1_29_20_59',
#HFM Bend 253950.0
'2016_1_29_21_3']

                                   
fout = open('/nfs/xf05id1/data/beamlineData/HFMbend/20160129_HFMy0_Pt.txt','w')

plottitle = 'Study Data'
pyplot.figure(1, figsize=(30,20))

bestpeakint = 0
bestwidth = 99999


outtext = 'fileprefix\tringcur\ttaper\televation\tpeakint\tpeakwidth\tpeakenergy\n'
fout.write(outtext)  

scannum=0
for fileprefix in fileprefixList:
    x, y, scanproperty = srxpeak.dataread(fileprefix=fileprefix, printarray=False, scriptname='srx-gc-slit-scan-v2.py', xcol = 2, ycol = 14)

    YmaxYvalue, YmaxXvalue, Ymaxindex, peakwidth = srxpeak.peakfind(xarray = x, yarray= y)
    
    y=y-1e-7
    a, b, c, fwhm = srxpeak.peakfit_gaussian(xarray = x, yarray= y, scanid= fileprefix, showplot = True, bkgsub=False, reverse=False, a=3e-7, b=0.3, c=0.05)     

    outtext = fileprefix+'\t'+ str(YmaxYvalue) \
                        +'\t'+ str(peakwidth) \
                        +'\t'+ str(YmaxXvalue) \
                        +'\t'+ str(fwhm) \
                        +'\n'

    pyplot.xlabel('x (mm)')
    pyplot.ylabel('Intensity')
    pyplot.title(plottitle)

    pyplot.plot(x, y, '+-', label=fileprefix+ ':' \
                                       +'; peakint=' + str(YmaxYvalue) \
                                       +' peakwidth='+ str(peakwidth) \
                                       +' peakenergy='+ str(YmaxXvalue)\
                                       +' fwhm='+ str(fwhm))
                                       
    fout.write(outtext)
    
fout.close()
pyplot.legend(loc=1)
pyplot.show() 


    
                            