# -*- coding: utf-8 -*-
"""
Created on Sun Nov  8 18:28:13 2015

@author: xf05id1
"""
import time


bshopen=PV('XF:05IDB-PPS:1{PSh:4}Cmd:Opn-Cmd')
bshclose=PV('XF:05IDB-PPS:1{PSh:4}Cmd:Cls-Cmd')
bshsta=PV('XF:05IDB-PPS:1{PSh:4}Sts:Cls-Sts')


def shutterclose():
    print 'Done with this XRF 2D map. Closing shutter for position change.'
    bshclose.put(1) 
    time.sleep(2)
    while bshsta.get() == 0:
        print 'shutter did not close, executing closing command again.'        
        bshclose.put(1)
        time.sleep(2)

    time.sleep(2)
        
    print 'Shutter closed.'

def shutteropen():
    print 'Open shutter for collecting XRF 2D map.'
        
    bshopen.put(1)
    time.sleep(2)
    while bshsta.get() == 1:
        print 'shutter did not open, executing opening command again.' 
        bshopen.put(1)
        time.sleep(2)

    time.sleep(2)

    print 'Shutter opend.'


shutteropen()
#%run ./srx-2dscan-sdd-timeout.py --detname=XF:05IDA{IM:1} --xstart=-90 --xnumstep=39 --xstepsize=0.5 --ystart=-10 --ynumstep=39 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam --checkcryo
%run ./srx-2dscan-sdd-timeout.py --detname=XF:05IDA{IM:1} --xstart=-90 --xnumstep=2 --xstepsize=0.5 --ystart=-10 --ynumstep=2 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam --checkcryo

shutterclose()
#time.sleep(300)

time.sleep(10)

shutteropen()
#%run ./srx-2dscan-sdd-timeout.py --detname=XF:05IDA{IM:1} --xstart=-90 --xnumstep=39 --xstepsize=0.5 --ystart=10 --ynumstep=39 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam --checkcryo

%run ./srx-2dscan-sdd-timeout.py --detname=XF:05IDA{IM:1} --xstart=-90 --xnumstep=2 --xstepsize=0.5 --ystart=10 --ynumstep=2 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam --checkcryo
#
#time.sleep(300)
#
#%run ./srx-2dscan-sdd-timeout.py --detname=XF:05IDA{IM:1} --xstart=-90 --xnumstep=39 --xstepsize=0.5 --ystart=30 --ynumstep=39 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam --checkcryo
#time.sleep(300)
#
#%run ./srx-2dscan-sdd-timeout.py --detname=XF:05IDA{IM:1} --xstart=-90 --xnumstep=39 --xstepsize=0.5 --ystart=50 --ynumstep=39 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam --checkcryo
#time.sleep(300)
#
#%run ./srx-2dscan-sdd-timeout.py --detname=XF:05IDA{IM:1} --xstart=-90 --xnumstep=39 --xstepsize=0.5 --ystart=70 --ynumstep=39 --ystepsize=0.5 --wait=0.1 --acqtime=0.5 --acqnum=1 --checkbeam --checkcryo
#time.sleep(300)
