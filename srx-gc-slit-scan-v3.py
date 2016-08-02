#! /usr/bin/env /usr/bin/python2.7
#original gjw
#modified 2015/03/02 by ycchen, Wayne fixed the SSA blades PV names' assignment. Updated those PV names.

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
        count = int(math.ceil( (float(end)-float(start))/float(inc) ))+1    
        print int(math.ceil( (float(end)-float(start))/float(inc) ))
    L = [None,] * count 
    p = pow(10,p) 
    start = start*p
    end = end*p
    inc = inc*p
        
    L[0] = float(start)/p
    for i in xrange(1,count):
        print i
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

simulate=False


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

def main(argv=None):
    global simulate
    global fp
    global shut_open
    global current

    #parse command line options
    usage = "usage: %prog [options]\nData files are written to /data/<year>/<month>/<day>/"
    parser = OptionParser(usage)
    parser.add_option("--slitname", action="store", type="string", dest="motname", help="valid options: wb, pb, ssa")
    parser.add_option("--detname", action="store", type="string", dest="detname", help="detector PV base")
    parser.add_option("--xstart", action="store", type="float", dest="xo", help="starting X position")
    parser.add_option("--xnumstep", action="store", type="int", dest="Nx", help="number of steps in X")
    parser.add_option("--xstepsize", action="store", type="float", dest="dx", help="step size in X")
    parser.add_option("--ystart", action="store", type="float", dest="yo", help="starting Y position")
    parser.add_option("--ynumstep", action="store", type="int", dest="Ny", help="number of steps in Y")
    parser.add_option("--ystepsize", action="store", type="float", dest="dy", help="step size in Y")
    parser.add_option("--hsize", action="store", type="float", dest="hs", help="slit size in horizontal")
    parser.add_option("--vsize", action="store", type="float", dest="vs", help="slit size in vertical")
    parser.add_option("--wait", action="store", type="float", dest="stall", help="wait at each step [seconds]")
    parser.add_option("--simulate", action="store_true", dest="sim", default=False, help="simulate motor moves")
    parser.add_option("--checkbeam", action="store_true", dest="checkbeam", default=False, help="only acquire when beam is on")

    (options,args) = parser.parse_args()

    #open log file
    D0=time.localtime()[0]
    D1=time.localtime()[1]
    D2=time.localtime()[2]
    D3=time.localtime()[3]
    D4=time.localtime()[4]
    cd=os.getcwd()
    
    filedir = '/nfs/xf05id1/data/' 
    
    if sys.argv[0][0]=='.':
        out_filename=filedir+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'log_'+repr(D3)+'_'+repr(D4)+'_'+\
         string.split(string.strip(sys.argv[0],'./'),'/')[0]+'.txt'
    else:
        out_filename=filedir+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'log_'+repr(D3)+'_'+repr(D4)+'_'+\
         string.split(string.strip(sys.argv[0],'./'),'/')[5]+'.txt'
    try:
        os.chdir(filedir+repr(D0))
    except OSError:
        try:    
            os.mkdir(filedir+repr(D0))
        except Exception:
            print 'cannot create directory: '+'/data/'+repr(D0)
            sys.exit()

    try:
        os.chdir(filedir+repr(D0)+'/'+repr(D1))
    except OSError:
        try:
            os.mkdir(filedir+repr(D0)+'/'+repr(D1))
        except Exception:
            print 'cannot create directory: '+'/data/'+repr(D0)+'/'+repr(D1)
            sys.exit()
    try:
        os.chdir(filedir+repr(D0)+'/'+repr(D1)+'/'+repr(D2))
    except OSError:
        try:
            os.mkdir(filedir+repr(D0)+'/'+repr(D1)+'/'+repr(D2))
        except Exception:
            print 'cannot create directory: '+filedir+repr(D0)+'/'+repr(D1)+'/'+repr(D2)
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
        print "must provide slit pv base, e.g., 'XF:28IDA-OP:1{Slt:MB1-Ax:T}'"
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

    if options.motname=='wb':
        slit=srxslit.nsls2slit(ib='XF:05IDA-OP:1{Slt:1-Ax:I}',\
         ob='XF:05IDA-OP:1{Slt:1-Ax:O}',tb='XF:05IDA-OP:1{Slt:1-Ax:T}',\
         bb='XF:05IDA-OP:1{Slt:1-Ax:B}')
    elif options.motname=='pb':
        slit=srxslit.nsls2slit(ib='XF:05IDA-OP:1{Slt:2-Ax:I}',ob='XF:05IDA-OP:1{Slt:2-Ax:O}')
    elif options.motname=='ssa':
#       slit=srxslit.nsls2slit(ib='XF:05IDB-OP:1{Slt:SSA-Ax:T}',\
#        ob='XF:05IDB-OP:1{Slt:SSA-Ax:B}',tb='XF:05IDB-OP:1{Slt:SSA-Ax:O}',\
#        bb='XF:05IDB-OP:1{Slt:SSA-Ax:I}')
        slit=srxslit.nsls2slit(ib='XF:05IDB-OP:1{Slt:SSA-Ax:I}',\
         ob='XF:05IDB-OP:1{Slt:SSA-Ax:O}',tb='XF:05IDB-OP:1{Slt:SSA-Ax:T}',\
         bb='XF:05IDB-OP:1{Slt:SSA-Ax:B}')
#        diode=PV('XF:05IDA{IM:1}Cur:I0-I')
        diode=PV('XF:05IDD-BI:1{Mscp:1-Cam:1}Stats1:Total_RBV')
    else:
        print "no valid slit options found on command line"
        sys.exit()
    #transmission
    #check command line options
    if options.yo == None:
        print "must provide a starting point in the vertical"
        sys.exit()
    else:   
        yo = options.yo
    if options.xo == None:
        print "must provide a starting point in the horizontal"
        sys.exit()
    else:   
        xo = options.xo
    if options.dx == None:
        dx = 0.00000001
    else:
        dx = options.dx
    if options.dy == None:
        dy = 0.00000001
    else:
        dy = options.dy
    if options.Nx == None:
        Nx = 0
    else:
        Nx = options.Nx
    if options.Ny == None:
        Ny = 0
    else:
        Ny = options.Ny
    if options.stall == None:
        twait = 0.
    else:
        twait = options.stall
    if options.hs is not None:
        if options.sim is False:
            slit.hsize(options.hs)
    if options.vs is not None:
        if options.sim is False:
            slit.vsize(options.vs)
    if options.motname=='pb' or options.motname=='wb':
        diode0=PV(detstr+':DataRead_Ch1')
        diode1=PV(detstr+':DataRead_Ch2')
        diode2=PV(detstr+':DataRead_Ch3')
        diode3=PV(detstr+':DataRead_Ch4')
    else:
        diode0=PV(detstr+':Current1:MeanValue_RBV')
        diode1=PV(detstr+':Current2:MeanValue_RBV')
        diode2=PV(detstr+':Current3:MeanValue_RBV')
        diode3=PV(detstr+':Current4:MeanValue_RBV')
        
    traj_o_x=PV('SR:C31-{AI}Aie5-2:Offset-x-Cal')
    traj_o_y=PV('SR:C31-{AI}Aie5-2:Offset-y-Cal')
    traj_a_x=PV('SR:C31-{AI}Aie5-2:Angle-x-Cal')
    traj_a_y=PV('SR:C31-{AI}Aie5-2:Angle-y-Cal')
    shut_status=PV('SR:C05-EPS{PLC:1}Shutter:Sum-Sts')
    beam_current=PV('SR:C03-BI{DCCT:1}I:Total-I')
    shut_status.add_callback(cbf_shut)
    beam_current.add_callback(cbf_curr)
    shut_status.run_callbacks()
    beam_current.run_callbacks()

    str='Start time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    str='#[point #]\tX pos\tY pos\tch 1\tch 2\tch 3\tch 4\tbpm ox\tbpm oy\tbpm ax\tbpm ay\tdiff h\tdiff v\tib\tob\tbb\ttp'
    print str
    fp.write(str)
    fp.write('\n')
    str='# h size: %(hs)6.3f ; v size: %(vs)6.3f ; h center: %(hc)6.3f ; v center: %(vc)6.3f'%\
     {"hs":slit.hsize(),"vs":slit.vsize(),"hc":slit.hcen(),"vc":slit.vcen()}
    print str
    fp.write(str)
    fp.write('\n')
    if options.sim is True:
        str="      -----simulating motor moves and bursts-----"
        print str
        fp.write(str)
        fp.write('\n')
    time.sleep(2)

    #number of rows and columns completed by scan
    Ncol=Nrow=0
    LN=0

    #scan direction for x
    dir=1

    count = 0
    sigarray=list()
    #nested loops for scanning z,x,y
    for y in np.linspace(yo,yo+((Ny)*dy),Ny+1):
        sigarry=[]
        if Nrow%2==0:
            xs=0.+xo
            xe=((Nx+1)*dx)+xo-dx
            xi=dx
        else:
            xs=((Nx)*dx)+xo
            xe=0.+xo
            xi=-dx
        for x in np.linspace(xs,xe,Nx+1):
            if options.sim is False:
                h=slit.hcen(x)
                v=slit.vcen(y)
            time.sleep(twait)
            while ( options.checkbeam and (shut_open == False or beam_current == False)):
                print "Stopped.  Waiting for scan conditions to return to normal."
                time.sleep(60.)
            sig=0.
            if options.motname=='ssa':
                while sig == 0.:
                    sig=diode.get()
                    #sigarray.append([x,sig])
            signal0=signal1=signal2=signal3=0.
            while signal0==0.:
                signal0=diode0.get()            
            while signal1==0.:
                signal1=diode1.get()            
            while signal2==0.:
                signal2=diode2.get()            
            while signal3==0.:
                signal3=diode3.get()            
            if options.sim is False:
                str='[%(X)04d] at ( %(XC)8.3f , %(YC)8.3f ): %(d1)10.7e %(d2)10.7e %(d3)10.7e %(d4)10.7e %(ox)6.3f %(oy)6.3f %(ax)6.3f %(ay)6.3f %(in)7.4e %(out)7.4e %(down)7.4e %(IB)7.4e %(OB)7.4e %(TB)7.4e %(BB)7.4e'%{"IB":slit.ibraw(),"OB":slit.obraw(),"BB":slit.bbraw(),"TB":slit.tbraw(),"down":float(sig),"X":Ncol,"XC":float(slit.hcen()), "d1":float(signal0), "d2":float(signal1), "d3":float(signal2),"d4":float(signal3),'YC':float(slit.vcen()), 'ox':float(traj_o_x.get()), 'oy':float(traj_o_y.get()), 'ax':float(traj_a_x.get()), 'ay':float(traj_a_y.get()), 'in':(float(signal0)-float(signal1))/float(signal1), 'out':(float(signal2)-float(signal3))/float(signal3)}       
        
                print str
                fp.write(str)
                fp.write('\n')
            else:
                str='[%(X)04d] at ( %(XC)8.3f , %(YC)8.3f ): %(d1)10.7e %(d2)10.7e %(d3)10.7e %(d4)10.7e %(ox)6.3f %(oy)6.3f %(ax)6.3f %(ay)6.3f %(down)7.4e'%{"down":float(sig),"X":int(Ncol),"XC":float(x), "d1":float(signal0), "d2":float(signal1), "d3":float(signal2),"d4":float(signal3),'YC':float(y), 'ox':float(traj_o_x.get()), 'oy':float(traj_o_y.get()), 'ax':float(traj_a_x.get()), 'ay':float(traj_a_y.get())}      
                print str
                fp.write(str)
                fp.write('\n')
    
            Ncol=Ncol+1
        #M=0.
        #for m in range(0,len(sigarray)):
        #   if sigarray[m][1]>1.8e-7:
        #       M=M+float(sigarray[m][1])
        #MX=0.
        #for m in range(0,len(sigarray)):
        #   if sigarray[m][1]>1.8e-7:
        #       MX=MX+float(sigarray[m][0])*float(sigarray[m][1])
        #str="CoM detected at %6.3e"%(MX/M)
        #print str
        #fp.write(str)
        #fp.write('\n')
        Nrow=Nrow+1

    str='End time is '+time.asctime()
    print str
    fp.write(str)
    fp.write('\n')
    fp.close()
    if options.sim is False:
        slit.hcen(xo)
        slit.vcen(yo)

    return 0

if __name__ == "__main__":
    sys.exit(main())
