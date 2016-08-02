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
import SRXenergy
import math   

dbd_bragg=0.001    
dbd_c1r=0.001    
dbd_c2x=0.001    
dbd_ugap=0.001  

Ei = 6.5
Ef = 7.5
c2xi = 3.658
c2xf = 3.860
c1ri = -4.787
c1rf = -4.787

braggTAR=None
c1rTAR=None
c2xTAR=None
ugapTAR=None
    
braggFLAG = None
c1rFLAG= None
c2xFLAG = None
ugapFLAG = None  
    
#def cbfbragg(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
#    if indeadband(float(braggTAR),float(value),dbd_bragg)==1:
#        braggFLAG = 0
#    else:
#        braggFLAG = 1
#def cbfc1r(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
#    if indeadband(float(c1rTAR),float(value),dbd_c1r)==1:
#        c1rFLAG= 0
#    else:
#        c1rFLAG = 1
#def cbfc2x(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
#    if indeadband(float(c2xTAR),float(value),dbd_c2x)==1:
#        c2xFLAG = 0
#    else:
#        c2xFLAG = 1
#
#def cbfugap(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
#    if indeadband(float(ugapTAR),float(value),dbd_ugap)==1:
#        ugapFLAG = 0
#    else:
#        ugapFLAG = 1


##manual deadband
#def indeadband(com,act,dbd):
#    if math.fabs(math.fabs(com)-math.fabs(act))<float(dbd):
#        return 1 
#    else:
#        return 0    
    
def moveE(Energy, harmonicIN = 3, c2xIN = None, c1rIN = None, simulate=True, XoffsetIn = None):

    braggVAL=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.VAL')
    braggRBV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.RBV')

    c1rVAL=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:R1}Mtr.VAL')
    c1rRBV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:R1}Mtr.RBV')
    
    c2xVAL=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.VAL')
    c2xRBV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.RBV')     
        
    ugapVAL=PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos')
    ugapRBV=PV('SR:C5-ID:G1{IVU21:1-LEnc}Gap')
    ugapGO = PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Sw:Go')
    
    xoffsetflag = False

#    braggRBV.add_callback(cbfbragg)
#    print('here1')
#    braggRBV.run_callbacks()
#    print('here2')
#    
#    c1rRBV.add_callback(cbfc1r)
#    c1rRBV.run_callbacks()
#
#    c2xRBV.add_callback(cbfc2x)
#    c2xRBV.run_callbacks()
#
#    ugapRBV.add_callback(cbfugap)
#    ugapRBV.run_callbacks()
    
    #setup the traget positions for all motors
    if XoffsetIn == None:
        braggTAR, c2x, ugapTAR = SRXenergy.EtoAll(Energy, harmonic = harmonicIN, show=False)
    else:
        xoffsetflag = True
        braggTAR, c2x, ugapTAR = SRXenergy.EtoAll(Energy, harmonic = harmonicIN, show=False, Xoffset=XoffsetIn)

   #if user doesn't specify c2x and c1r, use the current values    

    if c1rIN == None:
        c1rTAR=c1rRBV.get()
    elif c1rIN == 'linear':
        c1rTAR=c1ri+(Energy-Ei)/(Ef-Ei)*(c1rf-c1ri)
    else:
        c1rTAR=c1rIN
    
    ###need to move this section    
    if xoffsetflag == True:
        print('here2!')
        c2xTAR=c2x
    elif c2xIN == None:
        c2xTAR=c2xRBV.get()
    elif c1rIN == 'linear':
        c1rTAR=c2xi+(Energy-Ei)/(Ef-Ei)*(c2xf-c2xi)
    else:
        c2xTAR=c2xIN
        
    #moving the motors
    print('current positions:')
    print(' Energy:', str(SRXenergy.BraggtoE(braggRBV.get(), show=False)), 'keV')
    print(' HDCM Bragg:', str(braggRBV.get()))
    print(' undulator gap:', str(ugapRBV.get()))
    print(' HDCM 1st crystal roll:', str(c1rRBV.get()))
    print(' HDCM 2nd crystal gap:', str(c2xRBV.get()))    
    
    print('moving the motors to:')
    print(' Energy:', str(Energy))
    print(' HDCM Bragg:', str(braggTAR))
    print(' undulator gap:', str(ugapTAR))
    print(' HDCM 1st crystal roll:', str(c1rTAR))
    print(' HDCM 2nd crystal gap:', str(c2xTAR))

    if simulate == False:
        
        c1rVAL.put(c1rTAR, wait=True)
        c2xVAL.put(c2xTAR, wait=True)
        braggVAL.put(braggTAR, wait=True)
           
        ugapVAL.put(ugapTAR, wait=True)    
        ugapGO.put(0)
        time.sleep(5)

        print('done moving the motors, current positions:')
        print(' Energy:', str(SRXenergy.BraggtoE(braggRBV.get(), show=False)), 'keV')
        print(' HDCM Bragg:', str(braggRBV.get()))
        print(' undulator gap:', str(ugapRBV.get()))
        print(' HDCM 1st crystal roll:', str(c1rRBV.get()))
        print(' HDCM 2nd crystal gap:', str(c2xRBV.get()))  
        
    else: 
        print('simulating, not moving the motors.')