#! /usr/bin/env /usr/bin/python2.7
#backwards compatible (i.e., reverts to X raster move Y, hfm, vhm scan if no Z 
#values given) three dimensional fast mirror scan.  Scan is likely to be very 
#fast with respect to motor heating issues.  use --wait command line option
#if two transverse stages are scanned with sub-millimeter steps
#add file logging

#ycchen 03/12/15, modified one line to include current readout from bpm02: if detstr=='xf05bpm03' or detstr=='xf05bpm04':
#drop electron BPM readbacks and add preliminary support for xspress3
#refine support for xspress3.  push configuration from script, write a single hdf5
#2016/02/23 gjw
#hack to support saturn for purposes of comparing energy pseudomotion

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
import srxslit
import SRXenergy

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
tar.append([])
tar[1].append(0.)
tar[1].append(1)
tar.append([])
tar[2].append(0.)
tar[2].append(1)
#deadband in motor units 
dbd = .001
#simulate motor moves
simulate=False

global shut_open
shut_open = False
global current
current = False
global T_stop
T_stop = False

def cbf_shut(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global shut_open
    if value==1:
        shut_open=True
    else:
        shut_open=False 
def cbf_curr(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global current 
    if value<50.:
        current=False
    else:
        current=True    
#callback to check on motor position
def cbfx(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    if indeadband(float(tar[0][0]),float(value),dbd)==1:
        tar[0][1] = 0
    else:
        tar[0][1] = 1
def cbfy(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    if indeadband(float(tar[1][0]),float(value),dbd)==1:
        tar[1][1] = 0
    else:
        tar[1][1] = 1
def cbfz(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    if indeadband(float(tar[2][0]),float(value),dbd)==1:
        tar[2][1] = 0
    else:
        tar[2][1] = 1
def cbf_temp(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    #thresh_temp=80.
    thresh_temp = 120.
    global T_stop
    if (value > thresh_temp):
        T_stop=True
    else:
        T_stop=False
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
    global T_stop
    dSi111=SRXenergy.d111
    dbragg=SRXenergy.dBragg

    #parse command line options
    usage = "usage: %prog [options]\nData files are written to /data/<year>/<month>/<day>/"
    parser = OptionParser(usage)
    parser.add_option("--wait", action="store", type="float", dest="stall", help="wait at each step [seconds]")
    parser.add_option("--config",action="store", type="string", dest="fname", help="name of config file")
    parser.add_option("--simulate", action="store_true", dest="sim", default=False, help="simulate motor moves and bursting")
    parser.add_option("--checkbeam", action="store_true", dest="checkbeam", default=False, help="only acquire when beam is on")
    parser.add_option("--acqtime", action="store", type="float", dest="acqt", help="image integration time [sec]")

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
        out_filename=fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'log_'+repr(D0)+'_'+repr(D1)+'_'+repr(D2)+'_'+repr(D3)+'_'+repr(D4)+'_'+\
         string.split(string.strip(sys.argv[0],'./'),'/')[0]+'.txt'
    else:
        out_filename=fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'log_'+repr(D0)+'_'+repr(D1)+'_'+repr(D2)+'_'+repr(D3)+'_'+repr(D4)+'_'+\
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
    try:
        os.chdir(fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'HDF5')
    except OSError:
        try:
            os.mkdir(fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'HDF5')
        except Exception:
            print 'cannot create directory: '+fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'HDF5'
            sys.exit()
#    H5path=fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/HDF5'
    H5path='/epics/data/2015-3/300226-2'
#    H5path='/epics/data/2015-3/in-house'  
        
    os.chdir(cd)
    fp.write('#')
    fp.write(', '.join(sys.argv))
    fp.write('\n')
    #open list of scan points
    try:
        fconfig=open(options.fname)
    except Exception:
        print "cannot open file containing scan points.  Error opening: "+options.fname
        sys.exit()

    fstr='#a default string'
    pN=0
    angle=list()
    ivu=list()
    t2gap=list()
    while fstr.rsplit().__len__() > 0:
        if (fstr[0] is not '#'):
            pN=pN+1
            angle.append(fstr.rsplit()[0])
            ivu.append(fstr.rsplit()[1])
            t2gap.append(fstr.rsplit()[2])
        fstr=fconfig.readline()
    fconfig.close()

    #initialize PVs and callbacks
    detstr='XF:05IDA{IM:1}'
    bmot = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.VAL',connection_timeout=4)
    bmot_cur = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.RBV',connection_timeout=4)
    bmot_stop = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.STOP',connection_timeout=4)
    umot = PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos',connection_timeout=4)
    umot_cur = PV('SR:C5-ID:G1{IVU21:1-LEnc}Gap',connection_timeout=4)
    umot_go = PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Sw:Go',connection_timeout=4)
    gmot = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.VAL',connection_timeout=4)
    gmot_cur = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.RBV',connection_timeout=4)
    gmot_stop = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.STOP',connection_timeout=4)
    shut_status=PV('SR:C05-EPS{PLC:1}Shutter:Sum-Sts',connection_timeout=4)
    beam_current=PV('SR:C03-BI{DCCT:1}I:Total-I',connection_timeout=4)
    bragg_temp=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}T-I',connection_timeout=4)
#    norm0=PV('XF:05IDD-BI:1{BPM:01}.S20',connection_timeout=4)
#    norm1=PV('XF:05IDD-BI:1{BPM:01}.S21',connection_timeout=4)
#    norm2=PV('XF:05IDD-BI:1{BPM:01}.S22',connection_timeout=4)
#    norm3=PV('XF:05IDD-BI:1{BPM:01}.S23',connection_timeout=4)

    wb=srxslit.nsls2slit(tb='XF:05IDA-OP:1{Slt:1-Ax:T}',bb='XF:05IDA-OP:1{Slt:1-Ax:B}',ib='XF:05IDA-OP:1{Slt:1-Ax:I}',ob='XF:05IDA-OP:1{Slt:1-Ax:O}')
    pb=srxslit.nsls2slit(ib='XF:05IDA-OP:1{Slt:2-Ax:I}',ob='XF:05IDA-OP:1{Slt:2-Ax:O}')
    ssa=srxslit.nsls2slit(tb='XF:05IDB-OP:1{Slt:SSA-Ax:T}', bb='XF:05IDB-OP:1{Slt:SSA-Ax:B}', ob='XF:05IDB-OP:1{Slt:SSA-Ax:O}',ib='XF:05IDB-OP:1{Slt:SSA-Ax:I}')
    x3acq=PV('dxpSaturn:mca1Start',connection_timeout=4)
    x3erase=PV('dxpSaturn:mca1Erase',connection_timeout=4)
    x3acqtime=PV('dxpSaturn:mca1.PRTM',connection_timeout=4)
    x3ch1roi0min=PV('dxpSaturn:mca1.R0LO',connection_timeout=4)
    x3ch1roi0max=PV('dxpSaturn:mca1.R0HI',connection_timeout=4)
    x3ch1roi0ct=PV('dxpSaturn:mca1.R0N',connection_timeout=4)
    x3ch1roi1min=PV('dxpSaturn:mca1.R1LO',connection_timeout=4)
    x3ch1roi1max=PV('dxpSaturn:mca1.R1HI',connection_timeout=4)
    x3ch1roi1ct=PV('dxpSaturn:mca1.R1N',connection_timeout=4)
    x3ch1roi2min=PV('dxpSaturn:mca1.R2LO',connection_timeout=4)
    x3ch1roi2max=PV('dxpSaturn:mca1.R2HI',connection_timeout=4)
    x3ch1roi2ct=PV('dxpSaturn:mca1.R2N',connection_timeout=4)
    #claim ROI 4 for our own use.  we will integrate over all 2048 channels.
    x3ch1roi3min=PV('dxpSaturn:mca1.R3LO',connection_timeout=4)
    x3ch1roi3max=PV('dxpSaturn:mca1.R3HI',connection_timeout=4)
    x3ch1roi3ct=PV('dxpSaturn:mca1.R3N',connection_timeout=4)

    dett=PV('XF:05IDD-ES:1{EVR:1-Out:FP3}Src:Scale-SP',connection_timeout=4)
    deti=PV('XF:05IDA{IM:1}Per-SP',connection_timeout=4)
    detinit=PV('XF:05IDA{IM:1}Cmd:Init',connection_timeout=4)
    det0 = PV(detstr+'Cur:I0-I',connection_timeout=4)
    det1 = PV(detstr+'Cur:I1-I',connection_timeout=4)
    det2 = PV(detstr+'Cur:I2-I',connection_timeout=4)
    det3 = PV(detstr+'Cur:I3-I',connection_timeout=4)

    bmot.info
    bmot_cur.info
    bmot_stop.info
    umot.info
    umot_cur.info
    umot_go.info
    gmot.info
    gmot_cur.info
    gmot_stop.info
    det0.info
    det1.info
    det2.info
    det3.info
    bragg_temp.info

    bmot_cur.add_callback(cbfx)
    bmot_cur.run_callbacks()
    umot_cur.add_callback(cbfy)
    umot_cur.run_callbacks()
    gmot_cur.add_callback(cbfz)
    gmot_cur.run_callbacks()
    shut_status.add_callback(cbf_shut)
    beam_current.add_callback(cbf_curr)
    shut_status.run_callbacks()
    beam_current.run_callbacks()
    bragg_temp.add_callback(cbf_temp)
    bragg_temp.run_callbacks()
    x3acqtime.put(options.acqt)
    x3ch1roi3min.put(0)
    x3ch1roi3max.put(2048)
    dett.put(3)
    #overhead on triggering F460
    deti.put(options.acqt*.9)
    detinit.put(1)

    #check command line options
    if options.stall == None:
        twait = 0.
    else:
        twait = options.stall

    str='#NSLS-II SRX'+time.asctime()
    fp.write(str)
    fp.write('\n')

    str='# Start time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    if options.sim is True:
        str="      -----simulating motor moves and bursts-----"
        print str
        fp.write(str)
        fp.write('\n')
    else:
        dett.put(4)
        time.sleep(2)
        dett.put(3)
                            
    str='# bragg: %(br)6.4f ; undulator: %(un)6.4f ; gap: %(cg)f ; ROI1 %(roi1i)d:%(roi1a)d ; ROI2 %(roi2i)d:%(roi2a)d ; ROI3 %(roi3i)d:%(roi3a)d'%\
     {"br":bmot_cur.get(),"un":umot_cur.get(), "cg":gmot_cur.get(),'roi1i':x3ch1roi0min.get(), 'roi1a':x3ch1roi0max.get(), 'roi2i':x3ch1roi1min.get(), 'roi2a':x3ch1roi1max.get(), 'roi3i':x3ch1roi2min.get(), 'roi3a':x3ch1roi2max.get()}
    print str
    fp.write(str)
    fp.write('\n')
    str="# --------------------" 
    print str
    fp.write(str)
    fp.write('\n')
    str="# bragg u-gap c-gap energy I0-1 I0-2 I0-3 I0-4 time ROI-1 ROI-2 ROI-3 ROI-4 intensity" 
    print str
    fp.write(str)
    fp.write('\n')
    LN=0
    oldsig=det0.get() 
    t0=time.time()
    sig0=0.
    sig1=0.
    sig2=0.
    sig3=0.
    nsig0=0.
    nsig1=0.
    nsig2=0.
    nsig3=0.
    for x in range(0,pN):
        tar[0][1] = 1
        tar[0][0] = float(angle[x])
        tar[1][1] = 1
        tar[1][0] = float(ivu[x])
        tar[2][1] = 1
        tar[2][0] = float(t2gap[x])
        #if tar[0][0] is the original position, raise "in position" flag
        if indeadband(float(tar[0][0]),float(bmot_cur.get()),dbd)==1:
            tar[0][1] = 0
        if indeadband(float(tar[1][0]),float(umot_cur.get()),dbd)==1:
            tar[1][1] = 0
        if indeadband(float(tar[2][0]),float(gmot_cur.get()),dbd)==1:
            tar[2][1] = 0
        if options.sim is False:
            bmot.put(tar[0][0])
            umot.put(tar[1][0])
            gmot.put(tar[2][0])
            time.sleep(1)
            umot_go.put(0)
        else:
            tar[0][1]=0
            tar[1][1]=0
            tar[2][1]=0
        while (tar[0][1] == 1) or (tar[1][1] == 1) or(tar[2][1] == 1):
            time.sleep(0.05)
            if LN > 400:
                umot_go.put(0)
                LN=0
            else:
                LN=LN+1
        if options.sim is False:
            time.sleep(twait)
            while ( options.checkbeam and (shut_open == False or beam_current == False)) or T_stop==True:
                print "Stopped.  Waiting for scan conditions to return to normal."
                if shut_open == False:
                    print "\t->shutter is closed"
                elif beam_current == False:
                    print "\t->Ring current is below threshold"
                elif T_stop==True:
                    print "\t->HDCM pitch motor is too hot"
                else:
                    print "\t->why not have a nice cup of tea or hit ctrl-C?"
                time.sleep(60.)
            x3erase.put(1)
            dett.put(4)
#            nsig0=norm0.get()
#            nsig1=norm1.get()
#            nsig2=norm2.get()
#            nsig3=norm3.get()
#??
#           sig0=sig1=sig2=sig3=3
            sig0=sig1=sig2=0
#            roits=x3ch1roi3ct.timestamp
#            for i in range(0,1):
            x3acq.put(1) 
#                while ( x3ch1roi3ct.get()==0.0 or x3ch1roi3ct.timestamp==roits):
            time.sleep(0.2)
            sig0=sig0+x3ch1roi0ct.get()
            sig1=sig1+x3ch1roi1ct.get()
            sig2=sig2+x3ch1roi2ct.get()
#                sig3=sig3+x3ch1roi3ct.get()
#                sig0=sig0+x3ch2roi0ct.get()+x3ch3roi0ct.get()
#                sig1=sig1+x3ch2roi1ct.get()+x3ch3roi1ct.get()
#                sig2=sig2+x3ch2roi2ct.get()+x3ch3roi2ct.get()
#                sig3=sig3+x3ch2roi3ct.get()+x3ch3roi3ct.get()
            roits=x3ch1roi3ct.timestamp
            signal0=float(det1.get())
            while (signal0==0.0):
                signal0=float(det1.get())
            sig3=float(det0.get())
            sig2=float(det2.get())
#            while(signal0 == oldsig):
#                signal0=det0.get()
#            oldsig=signal0
            dett.put(3)
        else:
            while ( options.checkbeam and (shut_open == False or beam_current == False)):
                print "Stopped.  Waiting for beam to return."
                time.sleep(60.)
            signal0=0.
            nsig1=0
            nsig2=0
            nsig3=0
        tn=time.time()-t0
        if options.sim is False:    
#            str=' %(B)8.4f %(U)8.4f %(G)8.3f %(E)8.2f %(C0)10.7e %(C1)10.7e %(C2)10.7e %(C3)10.7e %(T)d %(ROI1)d %(ROI2)d %(ROI3)d %(ROI4)d %(T1)10.7e'%{"B":float(bmot_cur.get()), "U":float(umot_cur.get()), "G":float(gmot_cur.get()), "C0":nsig0, "C1":nsig1, "C2":nsig2, "C3":nsig3, "ROI1":sig0,'T':tn,"ROI2":sig1,"ROI3":sig2,"ROI4":sig3,"T1":signal0,"E":12398.4 / (2 * 3.13029665951 * math.sin((bmot_cur.get()+0.323658778534)/180.*np.pi))}
            str=' %(B)8.4f %(U)8.4f %(G)8.3f %(E)8.2f %(C0)10.7e %(C1)10.7e %(C2)10.7e %(C3)10.7e %(T)d %(ROI1)d %(ROI2)d %(ROI3)e %(ROI4)e %(T1)10.7e'%{"B":float(bmot_cur.get()), "U":float(umot_cur.get()), "G":float(gmot_cur.get()), "C0":nsig0, "C1":nsig1, "C2":nsig2, "C3":nsig3, "ROI1":sig0,'T':tn,"ROI2":sig1,"ROI3":sig2,"ROI4":sig3,"T1":signal0,"E":12398.4 / (2 * dSi111 * math.sin((bmot_cur.get()+dbragg)/180.*np.pi))}

            print str
            fp.write(str)
            fp.write('\n')
        else:
            str=' B= %(B)8.4f U= %(U)8.4f G= %(G)8.3f : %(C0)10.7e %(C1)10.7e %(C2)10.7e %(C3)10.7e %(ROI)d %(T)d'%{"B":tar[0][0], "U":tar[1][0], "G":tar[2][0], "C0":signal0, "C1":nsig1, "C2":nsig2, "C3":nsig3, "ROI":x3ch1roi0ct.get(),'T':time.time()} 
            print str
            fp.write(str)
            fp.write('\n')

    str='#End time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    fp.close()

    bmot_cur.clear_callbacks()
    umot_cur.clear_callbacks()
    gmot_cur.clear_callbacks()
    shut_status.clear_callbacks()
    beam_current.clear_callbacks()
    bragg_temp.clear_callbacks()

    return 0

if __name__ == "__main__":
    sys.exit(main())
