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
import random
import SRXenergy
import string


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
    
    d111=SRXenergy.d111
    dBragg=SRXenergy.dBragg

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
    os.chdir(cd)
    fp.write('# ')
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
    det_ROI1_int = PV(detstr+'Stats1:Total_RBV')
    det_ROI2_int = PV(detstr+'Stats2:Total_RBV')
    det_ROI3_int = PV(detstr+'Stats3:Total_RBV')
    det_ROI4_int = PV(detstr+'Stats4:Total_RBV')
    det_imode = PV(detstr+'ImageMode')
    det_im_en = PV(detstr+'TIFF1:EnableCallbacks')
    det_im_path = PV(detstr+'TIFF1:FilePath')
    det_im_name = PV(detstr+'TIFF1:FileName')
    det_im_num = PV(detstr+'TIFF1:FileNumber')
    det_im_save = PV(detstr+'TIFF1:WriteFile')
    det_im_cap = PV(detstr+'TIFF1:Capture')

    #ring current
    ring_i = PV('SR:C03-BI{DCCT:1}I:Real-I')
    text =  '#@ '\
              +'ring_i = ' + str(ring_i.get()) + '\t' \
              +'\n'

    print text             
    fp.write(text) 
    

    #undulator real position, gap and taper
    u_real_ds_low = PV('SR:C5-ID:G1{IVU21:1}REAL_POSITION_DS_LOWER')
    u_real_ds_upp = PV('SR:C5-ID:G1{IVU21:1}REAL_POSITION_DS_UPPER')
    u_real_us_low = PV('SR:C5-ID:G1{IVU21:1}REAL_POSITION_US_LOWER')
    u_real_us_upp = PV('SR:C5-ID:G1{IVU21:1}REAL_POSITION_US_UPPER')

    text =  '#@ '\
              +'u_real_ds_low = ' + str(u_real_ds_low.get()) + '\t' \
              +'u_real_ds_upp = ' + str(u_real_ds_upp.get()) + '\t' \
              +'u_real_us_low = ' + str(u_real_us_low.get()) + '\t' \
              +'u_real_us_upp = ' + str(u_real_us_upp.get()) + '\t' \
              +'\n'

    print text             
    fp.write(text)    

    u_real_gap_avg = PV('SR:C5-ID:G1{IVU21:1}REAL_GAP_AVG')
    u_real_gap_ds = PV('SR:C5-ID:G1{IVU21:1}REAL_GAP_DS')
    u_real_gap_us = PV('SR:C5-ID:G1{IVU21:1}REAL_GAP_US')    
    u_real_tapper = PV('SR:C5-ID:G1{IVU21:1}REAL_GAP_TAPER')

    
    text = '#@ ' \
             +'u_real_gap_avg = ' + str(u_real_gap_avg.get()) + '\t' \
             +'u_real_gap_ds = ' + str(u_real_gap_ds.get()) + '\t' \
             +'u_real_gap_us = ' + str(u_real_gap_us.get()) + '\t' \
             +'u_real_tapper = ' + str(u_real_tapper.get()) + '\t' \
             +'\n'
    print text            
    fp.write(text)
    
    #undulator elivation, girder
    u_real_elevation_us = PV('SR:C5-ID:G1{IVU21:1}REAL_ELEVATION_US')
    u_real_elevation_ds = PV('SR:C5-ID:G1{IVU21:1}REAL_ELEVATION_DS')
    u_real_elevation_avg = PV('SR:C5-ID:G1{IVU21:1}REAL_ELEVATION_AVG')
    
    text = '#@ ' \
             +'u_real_elevation_us = ' + str(u_real_elevation_us.get()) + '\t' \
             +'u_real_elevation_ds = ' + str(u_real_elevation_ds.get()) + '\t' \
             +'u_real_elevation_avg = ' + str(u_real_elevation_avg.get()) + '\t' \
             +'\n'
    print text            
    fp.write(text)
    
    u_real_girder_lower_tilt = PV('SR:C5-ID:G1{IVU21:1}REAL_GIRDER_LOWER_TILT')
    u_real_girder_upper_tilt = PV('SR:C5-ID:G1{IVU21:1}REAL_GIRDER_UPPER_TILT')   
    text = '#@ ' \
             +'u_real_girder_lower_tilt = ' + str(u_real_girder_lower_tilt.get()) + '\t' \
             +'u_real_girder_upper_tilt = ' + str(u_real_girder_upper_tilt.get()) + '\t' \
             +'\n'
    print text            
    fp.write(text)
    
    
    #undulator offset
    u_offset_ds_low = PV('SR:C5-ID:G1{IVU21:1}OFFSET_DS_LOWER_NEW')
    u_offset_ds_upp = PV('SR:C5-ID:G1{IVU21:1}OFFSET_DS_UPPER_NEW')
    u_offset_us_low = PV('SR:C5-ID:G1{IVU21:1}OFFSET_US_LOWER_NEW')
    u_offset_us_upp = PV('SR:C5-ID:G1{IVU21:1}OFFSET_US_UPPER_NEW')
    
    u_gap_for_calc = PV('SR:C5-ID:G1{IVU21:1}GAP_TO_USE_FOR_CALC:RB')
    
    text = '#@ ' \
             +'u_offset_ds_low  = ' + str(u_offset_ds_low.get()) + '\t' \
             +'u_offset_ds_upp = ' + str(u_offset_ds_upp.get()) + '\t' \
             +'u_offset_us_low = ' + str(u_offset_us_low.get()) + '\t' \
             +'u_offset_us_upp = ' + str(u_offset_us_upp.get()) + '\t' \
             +'u_gap_for_calc = ' + str(u_gap_for_calc.get()) + '\t' \
             +'\n'
    print text            
    fp.write(text)

    #undulator positions, gap and taper
    u_ds_low = PV('SR:C5-ID:G1{IVU21:1}POSITION_DS_LOWER')
    u_ds_upp = PV('SR:C5-ID:G1{IVU21:1}POSITION_DS_UPPER')
    u_us_low = PV('SR:C5-ID:G1{IVU21:1}POSITION_US_LOWER')
    u_us_upp = PV('SR:C5-ID:G1{IVU21:1}POSITION_US_UPPER')
    
    text = '#@ ' \
             +'u_ds_low  = ' + str(u_ds_low.get()) + '\t' \
             +'u_ds_upp = ' + str(u_ds_upp.get()) + '\t' \
             +'u_us_low = ' + str(u_us_low.get()) + '\t' \
             +'u_us_upp = ' + str(u_us_upp.get()) + '\t' \
             +'\n'
    print text            
    fp.write(text)
        
    u_gap_avg = PV('SR:C5-ID:G1{IVU21:1}GAP_AVG')
    u_gap_ds = PV('SR:C5-ID:G1{IVU21:1}GAP_DS')
    u_gap_us = PV('SR:C5-ID:G1{IVU21:1}GAP_US')    
    u_gap_taper = PV('SR:C5-ID:G1{IVU21:1}GAP_TAPER')
    
    text = '#@ ' \
             +'u_gap_avg  = ' + str(u_gap_avg.get()) + '\t' \
             +'u_gap_ds = ' + str(u_gap_ds.get()) + '\t' \
             +'u_gap_us = ' + str(u_gap_us.get()) + '\t' \
             +'u_gap_taper = ' + str(u_gap_taper.get()) + '\t' \
             +'\n'
    print text            
    fp.write(text)

    u_girder_lower_tilt = PV('SR:C5-ID:G1{IVU21:1}GIRDER_LOWER_TILT')
    u_girder_upper_tile = PV('SR:C5-ID:G1{IVU21:1}GIRDER_UPPER_TILT')
    u_girder_tilt_error = PV('SR:C5-ID:G1{IVU21:1}GIRDER_TILT_ERROR')
    u_girder_tilt_limit = PV('SR:C5-ID:G1{IVU21:1}GIRDER_TILT_LIMIT')
    
    text = '#@ ' \
             +'u_girder_lower_tilt  = ' + str(u_girder_lower_tilt.get()) + '\t' \
             +'u_girder_upper_tile = ' + str(u_girder_upper_tile.get()) + '\t' \
             +'u_girder_tilt_error = ' + str(u_girder_tilt_error.get()) + '\t' \
             +'u_girder_tilt_limit = ' + str(u_girder_tilt_limit.get()) + '\t' \
             +'\n'
    print text            
    fp.write(text)
    
    u_elev_ct_us = PV('SR:C5-ID:G1{IVU21:1-LEnc:1}Pos')
    u_elev_offset_us = PV('SR:C5-ID:G1{IVU21:1-LEnc:1}Offset')
    u_elev_ct_ds = PV('SR:C5-ID:G1{IVU21:1-LEnc:6}Pos')
    u_elev_offset_ds = PV('SR:C5-ID:G1{IVU21:1-LEnc:6}Offset')

    text = '#@ ' \
             +'u_elev_ct_us  = ' + str(u_elev_ct_us.get()) + '\t' \
             +'u_elev_offset_us = ' + str(u_elev_offset_us.get()) + '\t' \
             +'u_elev_ct_ds  = ' + str(u_elev_ct_ds.get()) + '\t' \
             +'u_elev_offset_ds = ' + str(u_elev_offset_ds.get()) + '\t' \
             +'\n'
    print text            
    fp.write(text)

    elevation_us = (u_elev_ct_us.get() + u_elev_offset_us.get())/1000000
    elevation_ds = (u_elev_ct_ds.get() + u_elev_offset_ds.get())/1000000
    elevation_avg = (elevation_us+elevation_ds)/2
    elevation_dif = elevation_us-elevation_ds
    
    text = '#@ ' \
             +'elevation_us  = ' + str(elevation_us) + '\t' \
             +'elevation_ds = ' + str(elevation_ds) + '\t' \
             +'elevation_avg  = ' + str(elevation_avg) + '\t' \
             +'elevation_dif = ' + str(elevation_dif) + '\t' \
             +'\n'
    print text            
    fp.write(text)    
    

    xmot_cur.get(as_string = True)
    xmot_cur.add_callback(cbfx)
    xmot_cur.run_callbacks()
    det_acq.info
    det_exp.info
    det_ROI1_int.info
    print det_ROI1_int.get()
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
        det_im_name.put('energytest-2015-3')
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

#    display_list = np.zeros((Nx+1,2))

    text='# Start time is '+time.asctime()
    print text
    fp.write(text)
    fp.write('\n')
    if options.sim is True:
        text="#      -----simulating motor moves and bursts-----"
        print text
        fp.write(text)
        fp.write('\n')
    text="# Current position [mm]: %(XC)7.3f" %\
     {"XC":xmot_cur.get()}
    print text
    fp.write(text)
    fp.write('\n')
    text="# Starting scan at: %(XO)7.3f"%\
     {"XO":xo}
    print text
    fp.write(text)
    fp.write('\n')
    time.sleep(2)
    text="# #####"
    print text
    fp.write(text)
    fp.write('\n')
    text="# point_num\tmotor_pos\tenergy\tROI1_int\tROI2_int\tROI3_int\tROI4_int"
    print text
    fp.write(text)
    fp.write('\n')


    #number of rows and columns completed by scan
    Ncol=0
    LN=0

    #scan direction for x
    dir=1

    #intensity
    ROIint=[-1,-1,-1,-1]

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
            ROIint[0]=float(det_ROI1_int.get())
            ROIint[1]=float(det_ROI2_int.get())
            ROIint[2]=float(det_ROI3_int.get())
            ROIint[3]=float(det_ROI4_int.get())
            det_im_save.put(1)
        else:
            print "bang"
            ROIint[0]=random.randint(1000,100000)
            ROIint[1]=random.randint(100,10000)
            ROIint[2]=random.randint(100,10000)
            ROIint[3]=random.randint(100,10000)
        if options.sim is False:    
            text=' %(X)04d %(XC)8.3f %(E)8.3f %(RI0)10.7e %(RI1)10.7e %(RI2)10.7e %(RI3)10.7e'%{"X":Ncol,"XC":xmot_cur.get(), "RI0":ROIint[0],\
             "RI1":ROIint[1],"RI2":ROIint[2],"RI3":ROIint[3], "E":12.3984/(2*d111*np.sin((xmot_cur.get()+dBragg)*np.pi/180))}
            print text
            fp.write(text)
            fp.write('\n')
        else:
            text=' %(X)04d %(XC)8.3f %(RI0)10.7e %(RI1)10.7e %(RI2)10.7e %(RI3)10.7e'%{"X":Ncol,"XC":tar[0][0], "RI0":ROIint[0],\
             "RI1":ROIint[1],"RI2":ROIint[2],"RI3":ROIint[3]}
            print text
            fp.write(text)
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
    text='# End time is '+time.asctime()
    print text
    fp.write(text)
    fp.write('\n')
    fp.close()

    return 0

if __name__ == "__main__":
    sys.exit(main())
