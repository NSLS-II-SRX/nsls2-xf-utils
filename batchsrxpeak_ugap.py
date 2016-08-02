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

fileprefixList = ['2016_1_27_13_35', #0
                  '2016_1_27_13_42', #1
                  '2016_1_27_13_54', #2-beam dump
                  '2016_1_27_15_12', #3
                  '2016_1_27_15_18', #4-max saturation
                  '2016_1_27_15_22', #5-max saturation
                  '2016_1_27_15_28', #6 reduce camera exposure time from 0.005 to 0.0025
                  '2016_1_27_15_33', #7
                  '2016_1_27_15_38', #8                    
                  '2016_1_27_15_44', #9  
                  '2016_1_27_15_56', #10
                  '2016_1_27_16_6', #11
                  '2016_1_27_16_18', #12
                  '2016_1_27_16_28', #13
                  '2016_1_27_16_34', #14
                  '2016_1_27_16_40', #15
                  '2016_1_27_16_45', #16 changed roi on camera x +5 pixel
                  '2016_1_27_16_52' #17
                 ]
                                   
fout = open('/nfs/xf05id1/data/beamlineData/study/20160127_undulator/summary.txt','w')

plottitle = 'Study Data'


pyplot.figure(1, figsize=(30,20))
pyplot.xlabel('Energy (keV)')
pyplot.ylabel('Intensity')
pyplot.title(plottitle)

bestpeakint = 0
bestwidth = 99999

outtext = 'fileprefix\tringcur\ttaper\televation\tpeakint\tpeakwidth\tpeakenergy\n'
fout.write(outtext)  

scannum=0
for fileprefix in fileprefixList:
    x, y, scanproperty = srxpeak.dataread(fileprefix=fileprefix, printarray=False, xcol = 2, ycol = 4)

    print 'scannum:', scannum
    if scannum <= 3:
        y  = y/2
        scannum=scannum+1
    elif scannum == 4 or scannum == 5:
        scannum=scannum+1
        continue
    else:
        scannum=scannum+1

    print 'scannum:', scannum

    YmaxYvalue, YmaxXvalue, Ymaxindex, peakwidth = srxpeak.peakfind(xarray = x, yarray= y)
    a, b, c, d = srxpeak.peakfit_gaussian(xarray = x, yarray= y, scanid= fileprefix, showplot = False, bkgsub=False)     

    elevation_us = (float(scanproperty['u_elev_ct_us']) + float(scanproperty['u_elev_offset_us']))/1000000
    elevation_ds = (float(scanproperty['u_elev_ct_ds']) + float(scanproperty['u_elev_offset_ds']))/1000000
    elevation_avg = (elevation_us+elevation_ds)/2
    elevation_dif = elevation_us-elevation_ds

    if YmaxYvalue > bestpeakint:
        bestpeakint = YmaxYvalue
        bestpeakfile = fileprefix
        bestpeaktaper = scanproperty['u_real_tapper']
        bestpeakelevt = elevation_avg
    if peakwidth < bestwidth:
        bestwidth = peakwidth
        bestwidthfile = fileprefix
        bestwidthtaper = scanproperty['u_real_tapper']
        bestpeakelevat = elevation_avg

    outtext = fileprefix+'\t'+ scanproperty['ring_i'] \
                        +'\t'+ scanproperty['u_real_tapper'] \
                        +'\t'+ str(elevation_avg) \
                        +'\t'+ str(YmaxYvalue) \
                        +'\t'+ str(peakwidth) \
                        +'\t'+ str(YmaxXvalue) \
                        +'\n'

    pyplot.plot(x, y, '+', label=fileprefix+ ':' \
                                       #+'ring current ='+scanproperty['ring_i'] \
                                       +' taper='+scanproperty['u_real_tapper'] \
                                       +' elevation='+ str(elevation_avg)\
                                       +'; peakint=' + str(YmaxYvalue) \
                                       +' peakwidth='+ str(peakwidth) \
                                       +' peakenergy='+ str(YmaxXvalue))
                                       
                        
    fout.write(outtext)


outtext = '\nbestpeakint = ' +  str(bestpeakint) + ';bestpeakfile = ' + str(bestpeakfile) + ';bestpeaktaper = ' + str(bestpeaktaper) + ';bestpeakelevat = ' + str(bestpeakelevat)

print outtext
fout.write(outtext)
fout.close()

pyplot.legend(loc=1)
pyplot.show() 


    
                            