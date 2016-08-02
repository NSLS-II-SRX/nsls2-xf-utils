#! /usr/bin/env /usr/bin/python2.7
#backwards compatible (i.e., reverts to X raster move Y, hfm, vhm scan if no Z 
#values given) three dimensional fast mirror scan.  Scan is likely to be very 
#fast with respect to motor heating issues.  use --wait command line option
#if two transverse stages are scanned with sub-millimeter steps
#add file logging

import signal
import sys
import os
import time
from epics import PV
import math
from optparse import OptionParser
import string
import decimal
import matplotlib.pyplot as plt
import numpy as np

#replace range()
#floating point and inclusive
def frange(start,end=None,inc=None,p=None):
    if end == None:
        end = start + 0.
        start = 0.
    if inc == None:
        inc = 1.
    if p == None:
        p = 3
    if inc == 0:
        count = 1
    else:
        count = int(math.ceil( (end-start)/inc ))+1 
    L = [None,] * count 
    p = pow(10,p) 

    start = start*p
    end = end*p
    inc = inc*p

    L[0] = float(start)/p
    for i in xrange(1,count):
        L[i] = L[i-1] + float(inc)/p
    
    return L
#can we signal handle in python??
def sigint_handler(signal,frame):
    global simulate
    global fp
    if simulate != True:
        fp.close()
        print "!!!!!!!!!    stopped"
    else:
        print "Ctrl-C detected...exiting"
    sys.exit()
signal.signal(signal.SIGINT,sigint_handler)

#target array:  (xpos, at_position)(ypos, at_position)
tar = []
tar.append([])
tar[0].append(0.)
tar[0].append(1)
#deadband in motor units 
dbd = .001
#simulate motor moves
simulate=False

#callback to check on motor position
def cbfx(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    if indeadband(float(tar[0][0]),float(value),dbd)==1:
        tar[0][1] = 0
    else:
        tar[0][1] = 1
#manual deadband
def indeadband(com,act,dbd):
    if math.fabs(math.fabs(com)-math.fabs(act))<float(dbd):
        return 1 
    else:
        return 0
def main(argv=None):
    global dbd
    global simulate
    global fp

    #parse command line options
    usage = "usage: %prog [options]\nData files are written to ~<operator>/<year>/<month>/<day>/"
    parser = OptionParser(usage)
    parser.add_option("--motname", action="store", type="string", dest="motname", help="motor to scan")
    parser.add_option("--detname", action="store", type="string", dest="detname", help="detector to trigger")
    parser.add_option("--xstart", action="store", type="float", dest="xo", help="starting X position")
    parser.add_option("--xnumstep", action="store", type="int", dest="Nx", help="number of steps in X")
    parser.add_option("--xstepsize", action="store", type="float", dest="dx", help="step size in X")
    parser.add_option("--wait", action="store", type="float", dest="stall", help="wait at each step [seconds]")
    parser.add_option("--simulate", action="store_true", dest="sim", default=False, help="simulate motor moves and bursting")
    parser.add_option("--acqtime",action="store", type="float", dest="acqt", help="acquisition time")
    parser.add_option("--filename",action="store", type="str", dest="fname", help="base file name for data")

    (options,args) = parser.parse_args()

    #open log file
    D0=time.localtime()[0]
    D1=time.localtime()[1]
    D2=time.localtime()[2]
    D3=time.localtime()[3]
    D4=time.localtime()[4]
    cd=os.getcwd()
    fstr='/nfs/xf05id1/data/'
    if sys.argv[0][0]=='.':
        out_filename=fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'log_'+repr(D3)+'_'+repr(D4)+'_'+\
         string.split(string.strip(sys.argv[0],'./'),'/')[0]+'.txt'
    else:
        out_filename=fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'log_'+repr(D3)+'_'+repr(D4)+'_'+\
         string.split(string.strip(sys.argv[0],'./'),'/')[5]+'.txt'
    try:
        os.chdir(fstr+repr(D0))
    except OSError:
        try:    
            os.mkdir(fstr+repr(D0))
        except Exception:
            print 'cannot create directory: '+fstr+repr(D0)
            sys.exit()

    try:
        os.chdir(fstr+repr(D0)+'/'+repr(D1))
    except OSError:
        try:
            os.mkdir(fstr+repr(D0)+'/'+repr(D1))
        except Exception:
            print 'cannot create directory: '+fstr+repr(D0)+'/'+repr(D1)
            sys.exit()
    try:
        os.chdir(fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2))
    except OSError:
        try:
            os.mkdir(fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2))
        except Exception:
            print 'cannot create directory: '+fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)
            sys.exit()
    try:
        fp=open(out_filename,'a')
    except Exception:
        print 'cannot open file: '+out_filename
        sys.exit()
    os.chdir(cd)
    fp.write(', '.join(sys.argv))
    fp.write('\n')
    #initialize PVs and callbacks
    if options.motname == None:
#       xmotstr='XF:03IDA-OP{Mon:1-Ax:P}'
        xmotstr=''
        print "must provide motor pv base, e.g., 'XF:28IDA-OP:1{Slt:MB1-Ax:T}'"
        sys.exit()
    else:
        xmotstr=options.motname
    if options.detname == None:
#       detstr='XF:03IDA-BI{FS:1-CAM:1}'
        detstr=''
        print "must provide detector pv base, e.g., 'XF:28IDA-BI{URL:01}'"
        sys.exit()
    else:
        detstr=options.detname
    
    #transmission
    xmot = PV(xmotstr+'Mtr.VAL')
    xmot_cur = PV(xmotstr+'Mtr.RBV')
    xmot_stop = PV(xmotstr+'Mtr.STOP')
    det_acq = PV(detstr+'Acquire')
    det_exp = PV(detstr+'AcquireTime')
    det_ROI_int = PV(detstr+'Stats1:Total_RBV')
    det_imode = PV(detstr+'ImageMode')
    det_im_en = PV(detstr+'TIFF1:EnableCallbacks')
    det_im_path = PV(detstr+'TIFF1:FilePath')
    det_im_name = PV(detstr+'TIFF1:FileName')
    det_im_num = PV(detstr+'TIFF1:FileNumber')
    det_im_save = PV(detstr+'TIFF1:WriteFile')
    det_im_cap = PV(detstr+'TIFF1:Capture')

    

    xmot_cur.get(as_string = True)
    xmot_cur.add_callback(cbfx)
    xmot_cur.run_callbacks()
    det_acq.info
    det_exp.info
    det_ROI_int.info
    print det_ROI_int.get()
    print "readback is "+detstr+'Stats1:Total_RBV'
    print "motor PV is "+xmotstr+'Mtr.VAL'
    print "trigger PV is "+detstr+'Acquire'
    det_im_en.put(1)
    if det_acq.get() is not 0:
        det_acq.put(1)
    if options.acqt is not None:
        det_exp.put(options.acqt)
    else:
        det_exp.put(0.1)
    det_imode.put(0)
    det_im_cap.put(1)
    if options.fname is None:
        det_im_name.put('energytest')
    else:
        det_im_name.put(options.fname)

    #check command line options
    if options.xo == None:
        xo = xmot_cur.get()
    else:   
        xo = options.xo
    if options.dx == None:
        dx = 0.00000001
    else:
        dx = options.dx
    if options.Nx == None:
        Nx = 0
    else:
        Nx = options.Nx
    if options.stall == None:
        twait = 0.
    else:
        twait = options.stall

    display_list = np.zeros((Nx+1,2))

    str='Start time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    if options.sim is True:
        str="      -----simulating motor moves and bursts-----"
        print str
        fp.write(str)
        fp.write('\n')
    str="Current position [mm]: %(XC)7.3f" %\
     {"XC":xmot_cur.get()}
    print str
    fp.write(str)
    fp.write('\n')
    str="Starting scan at: %(XO)7.3f"%\
     {"XO":xo}
    print str
    fp.write(str)
    fp.write('\n')
    time.sleep(2)

    #number of rows and columns completed by scan
    Ncol=0
    LN=0

    #scan direction for x
    dir=1

    #intensity
    ROIint=-1

    count = 0
    #nested loops for scanning z,x,y
    for x in frange(0,Nx*dx,dx):
        tar[0][1] = 1
        tar[0][0] = x+xo
        #if tar[0][0] is the original position, raise "in position" flag
        if indeadband(float(tar[0][0]),float(xmot_cur.get()),dbd)==1:
            tar[0][1] = 0
        if options.sim is False:
            xmot.put(tar[0][0])
        else:
            tar[0][1]=0
        while (tar[0][1] == 1):
            time.sleep(.05)
        if options.sim is False:
            det_acq.put(1)
            while det_acq.get()==1:
                time.sleep(det_exp.get())   
            time.sleep(twait)
            ROIint=float(det_ROI_int.get())
            det_im_save.put(1)
        else:
            print "bang"
        if options.sim is False:    
            str=' [%(X)04d] at (X= %(XC)8.3f ): Integrated ROI signal is %(RI)10.7e '%{"X":Ncol,"XC":xmot_cur.get(), "RI":ROIint}
            print str
            fp.write(str)
            fp.write('\n')
        else:
            str=' [%(X)04d] at (X= %(XC)8.3f )'%{"X":Ncol,"XC":tar[0][0]}
            print str
            fp.write(str)
            fp.write('\n')
        Ncol=Ncol+1
    #   display_list[count,0] = x
#       display_list[count,0] = xmot_cur.get()
#       display_list[count,1] = ROIint
#       count = count+1


    #return to starting positions
#   if options.sim is False:
#       xmot.put(xo)
#       time.sleep(0.01)

    det_im_cap.put(0)
    det_im_save.put(0)
    str='End time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    fp.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
