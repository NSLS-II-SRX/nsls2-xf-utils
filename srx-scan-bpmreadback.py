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
import srxbpm

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
        xmot_stop.put(1)
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
#simulate motor moves
simulate=False

#check for instrument readiness
global shut_open
shut_open = False
global current
current = False

def cbf_shut(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global shut_open
    if value==1:
        shut_open=True
    else:
        shut_open=False
def cbf_curr(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global current
    if value<1.:
        current=False
    else:
        current=True

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
    global shut_open
    global current
    #deadband in motor units 
    dbd = .001

    #parse command line options
    usage = "usage: %prog [options]\nData files are written to /data/<year>/<month>/<day>/"
    parser = OptionParser(usage)
    parser.add_option("--motname", action="store", type="string", dest="motname", help="motor to scan")
    parser.add_option("--xstart", action="store", type="float", dest="xo", help="starting X position")
    parser.add_option("--xnumstep", action="store", type="int", dest="Nx", help="number of steps in X")
    parser.add_option("--xstepsize", action="store", type="float", dest="dx", help="step size in X")
    parser.add_option("--deadband", action="store", type="float", dest="dbd", help="software deadband for motion, default is 0.001 motor units")
    parser.add_option("--wait", action="store", type="float", dest="stall", help="wait at each step [seconds]")
    parser.add_option("--simulate", action="store_true", dest="sim", default=False, help="simulate motor moves and bursting")
    parser.add_option("--checkbeam", action="store_true", dest="checkbeam", default=False, help="only acquire when beam is on")
    parser.add_option("--samples", action="store", type="int", dest="Nsamp", default=10, help="number of samples")
    parser.add_option("--raw", action="store_true", dest="rawval", default=False, help="return dimensionless values for BPM positions")

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
    if xmotstr.rsplit('{')[1].rsplit('}')[0] == 'IVU21:1-Mtr:2':
        undpv=True
    else:
        undpv=False
    if options.dbd is not None:
        dbd=options.dbd
    if options.Nsamp==1:
        print "[WW] number of samples should be greater than one"
    #transmission
    traj_o_x=PV('SR:C31-{AI}Aie5-2:Offset-x-Cal')
    traj_o_y=PV('SR:C31-{AI}Aie5-2:Offset-y-Cal')
    traj_a_x=PV('SR:C31-{AI}Aie5-2:Angle-x-Cal')
    traj_a_y=PV('SR:C31-{AI}Aie5-2:Angle-y-Cal')
    xmot = PV(xmotstr+'Mtr.VAL')
    xmot_cur = PV(xmotstr+'Mtr.RBV')
    xmot_stop = PV(xmotstr+'Mtr.STOP')
    shut_status=PV('SR:C05-EPS{PLC:1}Shutter:Sum-Sts')
    beam_current=PV('SR:C03-BI{DCCT:1}I:Total-I')

    xmot_cur.get(as_string = True)
    xmot_cur.add_callback(cbfx)
    xmot_cur.run_callbacks()
    shut_status.add_callback(cbf_shut)
    beam_current.add_callback(cbf_curr)
    shut_status.run_callbacks()
    beam_current.run_callbacks()

    bpm1=srxbpm.nsls2bpm(bpm='bpm1')
    bpm2=srxbpm.nsls2bpm(bpm='bpm2')

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

    str='Start time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    if options.sim is True:
        str="      -----simulating motor moves and bursts-----"
        print str
        fp.write(str)
        fp.write('\n')
    str="# Current position: %(XC)7.3f" %\
     {"XC":xmot_cur.get()}
    print str
    fp.write(str)
    fp.write('\n')
    str="# Starting scan at: %(XO)7.3f"%\
     {"XO":xo}
    print str
    fp.write(str)
    fp.write('\n')
    str="#\t\t\t      bpm1 H  H-stddev    bpm1 V  V-stddev    bpm2 H  H-stddev    bpm2 V  V-stddev   e bpm\t x off  y off x angle y angle"
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
        try:
            ox=traj_o_x.get()
        except CA.Client.Exception:
            ox=12398
            continue
        try:
            oy=traj_o_y.get()
        except CA.Client.Exception:
            ox=12398
            continue
        try:
            ay=traj_a_y.get()
        except CA.Client.Exception:
            ay=12398
            continue
        try:
            ax=traj_a_x.get()
        except CA.Client.Exception:
            ax=12398
            continue
        while (tar[0][1] == 1):
            time.sleep(0.05)
        h1_array=np.zeros(options.Nsamp)
        v1_array=np.zeros(options.Nsamp)
        h2_array=np.zeros(options.Nsamp)
        v2_array=np.zeros(options.Nsamp)
        time.sleep(twait)
        tmp=-12398.
        bpm1_dict=bpm1.P()
        bpm2_dict=bpm2.P()
        for i in range(0,options.Nsamp):
            #a call to srxbpm.nsls2bpm.P() typically returns within 35us while a call to *.Pavg(1) takes hundreds of ms
            #stuff the "instaneous" position information into an ndarray and calculate mean and stddev later
            while(tmp==bpm1_dict['H']):
                time.sleep(0.1)
                bpm1_dict=bpm1.P()
                bpm2_dict=bpm2.P()
            if options.rawval is True:
                h1_array[i]=bpm1_dict['H']*bpm1._H_Cal
                v1_array[i]=bpm1_dict['V']*bpm1._V_Cal
                h2_array[i]=bpm2_dict['H']*bpm2._H_Cal
                v2_array[i]=bpm2_dict['V']*bpm2._V_Cal
            else:
                h1_array[i]=bpm1_dict['H']
                v1_array[i]=bpm1_dict['V']
                h2_array[i]=bpm2_dict['H']
                v2_array[i]=bpm2_dict['V']

            tmp=bpm1_dict['H']
        if options.sim is False:    
            str=' [%(X)04d] at (X= %(XC)9.4f ): %(H1)8.5f %(H1S)8.4e %(V1)8.5f %(V1S)8.4e %(H2)8.5f %(H2S)8.4e %(V2)8.5f %(V2S)8.4e\t\t%(OX)6.3f %(OY)6.3f %(AX)6.3f %(AY)6.3f'%{"X":Ncol,"XC":xmot_cur.get(), "OX":ox,"AX":ax,"OY":oy,"AY":ay,"H1":h1_array.mean(),"H1S":h1_array.std(),"V1":v1_array.mean(),"V1S":v1_array.std(),"H2":h2_array.mean(),"H2S":h2_array.std(),"V2":v2_array.mean(),"V2S":v2_array.std()}
            print str
            fp.write(str)
            fp.write('\n')
        else:
            str=' [%(X)04d] at (X= %(XC)9.4f ): %(H1)8.5f %(H1S)8.4e %(V1)8.5f %(V1S)8.4e %(H2)8.5f %(H2S)8.4e %(V2)8.5f %(V2S)8.4e\t\t%(OX)6.3f %(OY)6.3f %(AX)6.3f %(AY)6.3f'%{"X":Ncol,"XC":tar[0][0], "OX":ox,"AX":ax,"OY":oy,"AY":ay,"H1":h1_array.mean(),"H1S":h1_array.std(),"V1":v1_array.mean(),"V1S":v1_array.std(),"H2":h2_array.mean(),"H2S":h2_array.std(),"V2":v2_array.mean(),"V2S":v2_array.std()}
            print str
            fp.write(str)
            fp.write('\n')
        Ncol=Ncol+1


    str='End time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    fp.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
