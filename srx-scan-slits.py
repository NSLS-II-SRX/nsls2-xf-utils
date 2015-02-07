#! /usr/bin/env python 
#original gjw
#modified ycchen

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
	usage = "usage: %prog [options]\nData files are written to /data/<year>/<month>/<day>/"
	parser = OptionParser(usage)
	parser.add_option("--motname", action="store", type="string", dest="motname", help="motor to scan")
	parser.add_option("--detname", action="store", type="string", dest="detname", help="detector groups: wb, pb, bpm1")
	parser.add_option("--xstart", action="store", type="float", dest="xo", help="starting X position")
	parser.add_option("--xnumstep", action="store", type="int", dest="Nx", help="number of steps in X")
	parser.add_option("--xstepsize", action="store", type="float", dest="dx", help="step size in X")
	parser.add_option("--wait", action="store", type="float", dest="stall", help="wait at each step [seconds]")
	parser.add_option("--simulate", action="store_true", dest="sim", default=False, help="simulate motor moves and bursting")

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
#		xmotstr='XF:03IDA-OP{Mon:1-Ax:P}'
		xmotstr=''
		print "must provide motor pv base, e.g., 'XF:28IDA-OP:1{Slt:MB1-Ax:T}'"
		sys.exit()
	else:
		xmotstr=options.motname
	if options.detname == None:
#		detstr='XF:03IDA-BI{FS:1-CAM:1}'
		detstr=''
		print "must provide detector pv base, e.g., 'XF:28IDA-BI{URL:01}'"
		sys.exit()
	else:
		#detstr=options.detname
		slitoption=options.detname
		if slitoption == 'wb':
			diode1='XF:05IDA-BI{BPM:01}AH501:Current1'
			diode2='XF:05IDA-BI{BPM:01}AH501:Current2'
			diode3='XF:05IDA-BI{BPM:01}AH501:Current3'
			diode4='XF:05IDA-BI{BPM:01}AH501:Current4'
			det_acqname='XF:05IDA-BI:1{FS:1-Cam:1}Acquire'
			det_expname='XF:05IDA-BI:1{FS:1-Cam:1}AcquireTime'
			det_ROI_intname='XF:05IDA-BI:1{FS:1-Cam:1}Stats1:Total_RBV'
			det_imodename='XF:05IDA-BI:1{FS:1-Cam:1}ImageMode'
		elif slitoption == 'pb':
                        diode1='XF:05IDA-BI{BPM:02}AH501:Current1'
                        diode2='XF:05IDA-BI{BPM:02}AH501:Current2'
                        diode3='XF:05IDA-BI{BPM:02}AH501:Current3'
                        diode4='XF:05IDA-BI{BPM:02}AH501:Current4'
			det_acqname='XF:05IDA-BI:1{BPM:1-Cam:1}Acquire'
			det_expname='XF:05IDA-BI:1{BPM:1-Cam:1}AcquireTime'
			det_ROI_intname='XF:05IDA-BI:1{BPM:1-Cam:1}Stats1:Total_RBV'
			det_imodename='XF:05IDA-BI:1{BPM:1-Cam:1}ImageMode'
		elif slitoption =='bpm1':
			diode1='XF:05IDA{IM:1}Cur:I0-I'
			diode2='XF:05IDA{IM:1}Cur:I1-I'
			diode3='XF:05IDA{IM:1}Cur:I2-I'
			diode4='XF:05IDA{IM:1}Cur:I3-I'
		else:
			print 'specify reading slits e.g. wb'

	#transmission
	xmot = PV(xmotstr+'Mtr.VAL')
	xmot_cur = PV(xmotstr+'Mtr.RBV')
	xmot_stop = PV(xmotstr+'Mtr.STOP')
	if slitoption=='bpm1':
		diode1_pv = PV(diode1)
		diode2_pv = PV(diode2)
		diode3_pv = PV(diode3)
		diode4_pv = PV(diode4)
	else:
		det_acq=PV(det_acqname)
		det_exp=PV(det_expname)
		det_ROI_int=PV(det_ROI_intname)
		det_imode=PV(det_imodename)
		diode1_pv = PV(diode1+':MeanValue_RBV')
		diode2_pv = PV(diode2+':MeanValue_RBV')
		diode3_pv = PV(diode3+':MeanValue_RBV')
		diode4_pv = PV(diode4+':MeanValue_RBV')
		if det_acq.get() is not 0:
			det_acq.put(1)
		det_imode.put(0)
	xmot_cur.get(as_string = True)
	xmot_cur.add_callback(cbfx)
	xmot_cur.run_callbacks()
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

	display_list = np.zeros((Nx+1,5))


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
			if LN>1000:
				LN=0
				xmot.put(tar[0][0])
				LN=LN+1
				xmot.info
		if options.sim is False:

			time.sleep(twait)
			if slitoption=='bpm1':
				diode1_read=diode1_pv.get()			
				diode2_read=diode2_pv.get()			
				diode3_read=diode3_pv.get()			
				diode4_read=diode4_pv.get()			
			else:
				diode1_read = diode1_pv.get()
				diode2_read = diode2_pv.get()
				diode3_read = diode3_pv.get()
               		        diode4_read = diode4_pv.get()
				det_acq.put(1)
				while det_acq.get()==1:
					time.sleep(det_exp.get())
				time.sleep(twait)
				ROIint=float(det_ROI_int.get())
		else:
			print "bang"
		if options.sim is False:	
			str='[%(X)04d] at (X=%(XC)8.3f): diode1 %(d1)10.7e, diode2  %(d2)10.7e, diode3  %(d3)10.7e, diode4  %(d4)10.7e, ROI %(roi)10d'%{"X":Ncol,"XC":xmot_cur.get(), "d1":diode1_read, "d2":diode2_read, "d3":diode3_read,"d4":diode4_read,'roi':ROIint}		
	
			print str
			fp.write(str)
			fp.write('\n')
		else:
			str=' [%(X)04d] at (X=%(XC)8.3f)'%{"X":Ncol,"XC":tar[0][0]}
			print str
			fp.write(str)
			fp.write('\n')

		Ncol=Ncol+1
		if options.sim is False:
			display_list[count,0] = xmot_cur.get()
			display_list[count,1] = diode1_read
			display_list[count,2] = diode2_read
			display_list[count,3] = diode3_read
			display_list[count,4] = diode4_read
		else:
			display_list[count,0] = tar[0][0]
			display_list[count,1] = 0. 
			display_list[count,2] = 0.
			display_list[count,3] = 0.
			display_list[count,4] = 0.
			
		count = count+1


	#return to starting positions
	if options.sim is False:
		xmot.put(xo)
		time.sleep(0.01)

	str='End time is '+time.asctime()
	print str
	fp.write(str)
	fp.write('\n')
	fp.close()

#	plt.figure()
	#plt.plot(display_list[:,0],display_list[:,1])
	
#	plt.plot(display_list[:,0],display_list[:,1],color='r')
#	plt.plot(display_list[:,0],display_list[:,1],'go')
#	plt.plot(display_list[:,0],display_list[:,2],color='g')
#	plt.plot(display_list[:,0],display_list[:,3],color='b')
#	plt.plot(display_list[:,0],display_list[:,4],color='k') 
 
#	plt.show()
	return 0

if __name__ == "__main__":
	sys.exit(main())
