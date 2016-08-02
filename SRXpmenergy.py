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
import sys


#Ei = 6.5
#Ef = 7.5
#c2xi = 3.658
#c2xf = 3.860
#c1ri = -4.787
#c1rf = -4.787

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
    
def move(Energy, harmonicIN = None, XoffsetIN = SRXenergy.XoffsetCurrent, c2xIN = None, c1rIN = None, simulate=False, show=True):

    '''
    user input energy, move undulator gap, c1x and HDCM bragg
    Note:
        The default is choosing the highest harmonic and adjust c2x using the default Xoffset (taken from SRXenergy.XoffsetCurrent).
        It'd give error message if the energy is out of our range.
        It checks if the c1r, c2x and bragg are done moving, and if the u-gap break is on.    
    
    input:
        Energy: user defined energy as the target, in a unit of keV
        
    key words:
        harmonicIN: default is 'None'. program will choose the highest harmonic achievable for that energy range (recommended)
                    user can provide an alternative harmonic value if desired.
        XoffsetIN: default is taken from SRXenergy.XoffsetCurrent. This will determined the c2x target when moving energy (recommended). 
                   user can provide a user-defined value
        c2xIN: defualt is None. If user specify a value for c2xIN, this value will be used as a fixed c2x value, and XoffsetIN will be ignored.  
               if c2xIN == None and XoffsetIN == None, current c2x value will be used.
        c1rIN: default is None. If user doesn't specify c1r, use current c1r value (recommended)
        simulate: deault is False, meaning that the motors will move. If it is set to False, the motors will not move and users can check the calculation.       
    
    '''
    
    #dbd_bragg=0.001    
    #dbd_c1r=0.001    
    #dbd_c2x=0.001    
    dbd_ugap=0.001

    Energy = float(Energy)

    braggVAL=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.VAL')
    braggRBV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.RBV')
    braggMOV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.MOVN')

    c1rVAL=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:R1}Mtr.VAL')
    c1rRBV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:R1}Mtr.RBV')
    c1rMOV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:R1}Mtr.MOVN')
    
    c2xVAL=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.VAL')
    c2xRBV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.RBV')     
    c2xMOV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.MOVN')

        
    ugapVAL=PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos')
    ugapRBV=PV('SR:C5-ID:G1{IVU21:1-LEnc}Gap')
    ugapGO = PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Sw:Go')
    ugapbrkON=PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Rb:Brk')
  

    
    #xoffsetflag = False

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

    #calculate the right harmonic for undulator gap
    harmonictest=3
    if harmonicIN == None:
        #choose the right harmonic
        braggcal, c2xcal, ugapcal = SRXenergy.EtoAll(Energy, harmonic = harmonictest, show=False) 
        if ugapcal <=6.4:
            print('The energy you entered is too low. Minimum energy = 4.4 keV')
            sys.exit()
        while ugapcal >=6.4:
            harmonictest=harmonictest+2
            #print(harmonictest)
            braggcal, c2xcal, ugapcal = SRXenergy.EtoAll(Energy, harmonic = harmonictest, show=False)
            #print(ugapcal)
        harmonicIN = harmonictest-2
        if harmonicIN > 17:
            print('The energy you entered is too high. Maximum energy = 25.0 keV')
            sys.exit()                   
        print('using harmonic: '+str(harmonicIN))
    
    #setup the traget positions for all motors
    if XoffsetIN == None:
        braggTAR, c2x, ugapTAR = SRXenergy.EtoAll(Energy, harmonic = harmonicIN, show=False)
    else:
        braggTAR, c2x, ugapTAR = SRXenergy.EtoAll(Energy, harmonic = harmonicIN, show=False, Xoffset=XoffsetIN)


   #if user doesn't specify c1r, use current c1r value
    if c1rIN == None:
        c1rTAR=c1rRBV.get()
#    elif c1rIN == 'linear':
#        c1rTAR=c1ri+(Energy-Ei)/(Ef-Ei)*(c1rf-c1ri)
    else:
        c1rTAR=c1rIN
    
    if c2xIN != None:
        c2xTAR=c2xIN
    elif XoffsetIN != None:
        c2xTAR=c2x
    else: 
        print('Both XoffsetIN and c2xIN are "None". use current c2x value.')
        c2xTAR=c2xRBV.get()
 
    #moving the motors
    if show == True: 
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
        ugapVAL.put(ugapTAR, wait=True)    
        ugapGO.put(0)
        braggVAL.put(braggTAR, wait=True)
        time.sleep(1)

        #while (c1rRBV.get()-c1rVAL.get()) > dbd_c1r:
        if c1rMOV.get() == 1:
            print('waiting for c1r.')
        while c1rMOV.get() == 1:
            time.sleep(1)
        print('c1r in place')
 
        #while (c2xRBV.get()-c2xVAL.get()) > dbd_c2x: 
        if c2xMOV.get() == 1:
            print('waiting for c2x.')
        while c2xMOV.get() == 1:                   
            time.sleep(1)
        print('c2x in place')

        #while (braggRBV.get()-braggVAL.get()) > dbd_bragg:       
        if braggMOV.get() == 1:
            print('waiting for bragg.')
        while braggMOV.get() == 1: 
            time.sleep(1)
        print('bragg in place')

        #while (ugapVAL.get()-ugapRBV.get()) > dbd_ugap:
        if ugapbrkON.get() == 0:
            print('waiting for ugap.')
        while ugapbrkON.get() == 0:
            time.sleep(1)
        if ugapRBV.get() - ugapVAL.get() <= dbd_ugap:
            print('ugap in place')
        else:
            print('ugap position cannot be reached. Possible taper error. Check to see if ugap Correction Function is disabled')

        print('done moving the motors, current positions:')
        print(' Energy:', str(SRXenergy.BraggtoE(braggRBV.get(), show=False)), 'keV')
        print(' HDCM Bragg:', str(braggRBV.get()))
        print(' undulator gap:', str(ugapRBV.get()))
        print(' HDCM 1st crystal roll:', str(c1rRBV.get()))
        print(' HDCM 2nd crystal gap:', str(c2xRBV.get()))  
        
    else: 
        if show == True:        
            print('simulating, not moving the motors.')
        return harmonicIN