#! /usr/bin/env /usr/bin/python2.7 
#backwards compatible (i.e., reverts to X raster move Y, hfm, vhm scan if no Z 
#values given) three dimensional fast mirror scan.  Scan is likely to be very 
#fast with respect to motor heating issues.  use --wait command line option
#if two transverse stages are scanned with sub-millimeter steps
#add file logging

#by ycchen 03/12/15, change one line: 'det_acq = PV(detstr)' for it to work with bpm1&2 current readout

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
def sigtstp_handler(signal,frame):
    print "Ctrl-z detected.  Scan paused."
    raw_input('Press enter to resume.')
signal.signal(signal.SIGTSTP,sigtstp_handler)


#target array:  (xpos, at_position)(ypos, at_position)
tar = []
tar.append([])
tar[0].append(0.)
tar[0].append(1)
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
    #deadband in motor units 
    dbd = .001

    #parse command line options
    usage = "usage: %prog [options]\nData files are written to /data/<year>/<month>/<day>/"
    parser = OptionParser(usage)
    parser.add_option("--motname", action="store", type="string", dest="motname", help="motor to scan")
    parser.add_option("--detname", action="store", type="string", dest="detname", help="detector to trigger")
    parser.add_option("--xstart", action="store", type="float", dest="xo", help="starting X position")
    parser.add_option("--xnumstep", action="store", type="int", dest="Nx", help="number of steps in X")
    parser.add_option("--xstepsize", action="store", type="float", dest="dx", help="step size in X")
    parser.add_option("--deadband", action="store", type="float", dest="dbd", help="software deadband for motion, default is 0.001 motor units")
    parser.add_option("--wait", action="store", type="float", dest="stall", help="wait at each step [seconds]")
    parser.add_option("--simulate", action="store_true", dest="sim", default=False, help="simulate motor moves and bursting")
    parser.add_option("--acqtime", action="store", type="float", dest="acqt", help="SDD acquisition time at each step [seconds]")

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
    H5path='/epics/data/201507'
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
    if xmotstr.rsplit('{')[1].rsplit('}')[0] == 'IVU21:1-Mtr:2':
        undpv=True
    else:
        undpv=False
    if options.dbd is not None:
        dbd=options.dbd
    #transmission
    if undpv is False:
        xmot = PV(xmotstr+'Mtr.VAL')
        xmot_cur = PV(xmotstr+'Mtr.RBV')
        xmot_stop = PV(xmotstr+'Mtr.STOP')
    else:
        xmot = PV(xmotstr+'Inp:Pos')
        xmot_cur = PV(xmotstr.rsplit('{')[0]+'{IVU21:1-LEnc}Gap')
        xmot_stop = PV(xmotstr+'Sw:Go')
#   det_acq = PV(detstr+'Cur:I0-I')
    if 'IM' in detstr:
        det0_acq=PV(detstr)
        det1_acq=PV(detstr.replace('I0-I','I1-I'))
    else:
        det0_acq = PV(detstr)  
        det1_acq = None
    x3acq=PV('XSPRESS3-EXAMPLE:Acquire')
    x3erase=PV('XSPRESS3-EXAMPLE:ERASE')
    x3acqtime=PV('XSPRESS3-EXAMPLE:AcquireTime')
    x3acqnum=PV('XSPRESS3-EXAMPLE:NumImages')
    x3tmode=PV('XSPRESS3-EXAMPLE:TriggerMode')
    x3h5path=PV('XSPRESS3-EXAMPLE:HDF5:FilePath')
    x3h5fname=PV('XSPRESS3-EXAMPLE:HDF5:FileName')
    x3h5fnum=PV('XSPRESS3-EXAMPLE:HDF5:FileNumber')
    x3h5capture=PV('XSPRESS3-EXAMPLE:HDF5:Capture')
    x3ch1roi0min=PV('XSPRESS3-EXAMPLE:C1_MCA_ROI1_LLM')
    x3ch1roi0max=PV('XSPRESS3-EXAMPLE:C1_MCA_ROI1_HLM')
    x3ch1roi0ct=PV('XSPRESS3-EXAMPLE:C1_ROI1:Value_RBV')

    xmot_cur.get(as_string = True)
    xmot_cur.add_callback(cbfx)
    xmot_cur.run_callbacks()
    det0_acq.info
    if det1_acq is not None:
        det1_acq.info
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
    x3h5path.put(H5path)
    x3h5fname.put(repr(D3)+'_'+repr(D4)+'_')
    x3h5fnum.put(0)
    x3acqtime.put(options.acqt)
    x3acqnum.put(1)
    x3tmode.put(1)

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
            if undpv ==True:
                time.sleep(0.5)
                xmot_stop.put(0)
        else:
            tar[0][1]=0
        while (tar[0][1] == 1):
            if LN>1000:
                LN=0
                xmot.put(tar[0][0])
                LN=LN+1
                xmot.info
                if xmot.severity == 2:
                    str="\t scan stopped at "+xmot_cur.get()
                    print str
                    fp.write(str)
                    fp.write('\n')
                    raw_input("clear motor error and press enter (or ctrl-C to halt)")
                    xmot.put(tar[0][0])
                    time.sleep(twait)
        if options.sim is False:
            time.sleep(twait)
            x3h5capture.put(1)
            x3erase.put(1)
            x3acq.put(1)
            signal=[0.,0.]
            signal[0]=float(det0_acq.get())
            while(signal[0] == 0.):
                time.sleep(0.01)
                signal[0]=float(det0_acq.get())
            if det1_acq is not None:
                signal[1]=float(det1_acq.get())
                while(signal[1] == 0.):
                    time.sleep(0.01)
                    signal[1]=float(det1_acq.get())
            time.sleep(options.acqt)
        else:
            print "bang"
            signal=0.
        if options.sim is False:    
            sigstr='%(one)10.7e %(two)10.7e'%{'one':signal[0],'two':signal[1]}
            str=' [%(X)04d] at (X= %(XC)9.4f ): signal is %(RI)s '%{"X":Ncol,"XC":xmot_cur.get(), "RI":sigstr}
            print str
            fp.write(str)
            fp.write('\n')
        else:
            str=' [%(X)04d] at (X= %(XC)8.3f )'%{"X":Ncol,"XC":tar[0][0]}
            print str
            fp.write(str)
            fp.write('\n')
        Ncol=Ncol+1


    #return to starting positions
    if options.sim is False:
        xmot.put(xo)
        time.sleep(0.01)
        if undpv ==True:
            time.sleep(0.5)
            xmot_stop.put(0)

    str='End time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    fp.close()
#    xmot_cur.clear_callbacks()

    return 0

if __name__ == "__main__":
    sys.exit(main())
