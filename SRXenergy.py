# -*- coding: utf-8 -*-
"""
Created on Sat Apr 11 00:34:06 2015

@author: xf05id1
"""

from __future__ import print_function
import numpy
from scipy.interpolate import InterpolatedUnivariateSpline
from epics import PV
import time
import bindingEnergy as be

#energy calibration parameters
#########2015 cycle1
d111 = 3.12973605055
dBragg = 0.313172406312
C2Xcal=4
T2cal=13.389
UCalibDir = '/nfs/xf05id1/UndulatorCalibration/'
infile = 'SRXUgapCalibration20150411_final.text' 

########2015 cycle2
d111 = 3.13029665951
dBragg = 0.323658778534
C2Xcal=3.6
#T2cal=12.8416682292  #2015/06/17
T2cal=12.8847915941 #2015/06/18

UCalibDir = '/nfs/xf05id1/UndulatorCalibration/'
infile = 'SRXUgapCalibration20150411_final.text' 

#######2015 cycle3
d111 = 3.12964794061 #2015/10/05
#dBragg = 0.323658778534 +0.0235 offset discoverred in the beginning of the cycle
dBragg = 0.323341791985 #2015/10/05
#C1Rcal=-4.86 #2015/10/05; BPM1, not required for calculating energy axis, fixed value
C1Rcal=-4.823 #2015/10/05; endstation not required for calculating energy axis, fixed value

C2Xcal=3.6 #2015/10/05 BPM1 
T2cal= 13.911608051 #2015/10/05 BPM1
XoffsetCurrent=25.2521 #upto 2015/11/5 unknown timing
#XoffsetCurrent=25.29 #2015/11/5 
#C2Xcal=4.2 #2015/10/05 endstation
#T2cal= 10.4574785277 #2015/10/05 endstation, C2P = -19.2914

#d111=3.12933292083  #2015/11/10 exclude Cr
#dBragg=0.323416238671  #2015/11/10 exclude Cr
d111= 3.12961447804    #2015/11/10 (Se, Cu, Fe, Cr, Ti)
dBragg=0.322545952931  #2015/11/10 (Se, Cu, Fe, Cr, Ti)
C1Rcal=-4.83257845217  #2015/11/10, bpm1
C2Xcal=3.6             #2015/11/10 BPM1
T2cal= 13.4691878989   #2015/11/10 BPM1
#XoffsetCurrent=25.2521 


##everthing up to here was done with HDCM Y = -14.498

####################################################
##calibration for HDCM Y = -17.498

C1Rcal = -4.84521119077 #2015/11/11
C2Xcal = 3.6 #2015/11/11
T2cal = 13.4789609239 #2015/11/11

UCalibDir = '/nfs/xf05id1/UndulatorCalibration/'
infile = 'SRXUgapCalibration20150411_final.text' 

#####################################################
##back to HDCM Y = -14.498
C2Xcal = 3.6
T2cal= 13.463294326

###################################################
d111= 3.12924894907   #2016/1/27 (Se, Cu, Fe, Ti)
dBragg=0.315532509387  #2016/1/27 (Se, Cu, Fe, Ti)
C1Rcal =  -4.88949983261 #2016/1/29
C2Xcal = 3.6 #2016/1/29
T2cal = 13.7187120636 #2016/1/29


def whd111(*args, **kwargs):
    print(d111)
    return d111

def whdBragg(*args, **kwargs):
    print(dBragg)    
    return dBragg
    
def whC2X(*args, **kwargs):
    print(C2Xcal, T2cal)    
    return C2Xcal, T2cal

def whC1R(*args, **kwargs):
    print(C1Rcal)    
    return C1Rcal

def EtoAll(Energy, harmonic = 3, Xoffset=XoffsetCurrent, d111=d111, dBragg=dBragg, 
                      C2Xcal=C2Xcal, T2cal=T2cal, 
                      UCalibDir=UCalibDir, infile=infile, show=True):
    '''input: Energy, 
       optional input: Xoffset - beam offset in x to obatin the corresponding C2X, default 25 mm
       based on calibrated d111, Bragg offset (dBragg), C2X calibration,
       return BraggRBV, C2X, ugap for this energy
       syntax: BraggRBV, C2X, ugap = SRXenergy.EtoAll(Energy, Xoffset=[value])'''
    
    #calculate Bragg RBV    
    BraggRBV = numpy.arcsin((12.3984/float(Energy))/(2*d111))/numpy.pi*180-dBragg

    #calculate C2X    
    Bragg=BraggRBV+dBragg
    T2=Xoffset*numpy.sin(Bragg*numpy.pi/180)/numpy.sin(2*Bragg*numpy.pi/180)
    dT2=T2-T2cal
    C2X=C2Xcal-dT2    
    
    #calculate undulator gap
    f = open(UCalibDir+infile, 'r')
    next(f)
    uposlistIn=[]
    elistIn=[]
    for line in f:
        num = [float(x) for x in line.split()]
        uposlistIn.append(num[0])
        elistIn.append(num[1]) 
    etoulookup = InterpolatedUnivariateSpline(elistIn, uposlistIn)
    ugap= etoulookup(float(Energy)/harmonic)
    
    if show == True:    
        print('For energy = ', Energy, 'keV')
        print('Bragg RBV = ', numpy.round(BraggRBV, 4), 'deg')
        print('C2X = ', numpy.round(C2X, 4), 'mm; with beam x offset set to:', Xoffset, 'mm')
        print('harmonic = ', harmonic)    
        print('ugap =', ugap)
    
    return BraggRBV, C2X, ugap         
    
def BraggtoE(BraggRBV, d111=d111, dBragg=dBragg, show = True):

    Energy = 12.3984/(2*d111*numpy.sin((BraggRBV+dBragg)*numpy.pi/180))
    if show == True:
        print('at BraggRBV =', BraggRBV, ',Energy = ', Energy)
    return Energy
    
def UgaptoE(ugap, harmonic=3., UCalibDir=UCalibDir, infile=infile, show = True):
    f = open(UCalibDir+infile, 'r')
    next(f)
    uposlistIn=[]
    elistIn=[]
    for line in f:
        num = [float(x) for x in line.split()]
        uposlistIn.append(num[0])
        elistIn.append(num[1]) 
    utoelookup = InterpolatedUnivariateSpline(uposlistIn, elistIn)
    fundemental = utoelookup(ugap)
    energy = fundemental*harmonic
    
    if show == True:
        print('energy =', energy, 'with harmonic = ', harmonic, 'fundamental E = ', fundemental)
    
    return energy, fundemental

def C2XtoXoffset(C2X, BraggRBV, d111=d111, dBragg=dBragg, T2cal=T2cal,show = True):
    
    Bragg=BraggRBV+dBragg        

    dT2=C2Xcal-C2X
    T2=dT2+T2cal
    XoffsetVal=T2/(numpy.sin(Bragg*numpy.pi/180)/numpy.sin(2*Bragg*numpy.pi/180))

    if show == True:
        print(' with C2X = ', C2X, '\n',
              'with Bragg = ', BraggRBV, '\n',
                'Xoffset = ', XoffsetVal)
    return XoffsetVal

