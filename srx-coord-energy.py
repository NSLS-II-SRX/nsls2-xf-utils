#! /usr/bin/env /usr/bin/python2.7
#backwards compatible (i.e., reverts to X raster move Y, hfm, vhm scan if no Z 
#values given) three dimensional fast mirror scan.  Scan is likely to be very 
#fast with respect to motor heating issues.  use --wait command line option
#if two transverse stages are scanned with sub-millimeter steps
#add file logging

#ycchen 03/12/15, modified one line to include current readout from bpm02: if detstr=='xf05bpm03' or detstr=='xf05bpm04':


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

	#parse command line options
	usage = "usage: %prog [options]\nData files are written to /data/<year>/<month>/<day>/"
	parser = OptionParser(usage)
	parser.add_option("--detname", action="store", type="string", dest="detname", help="detector to trigger")
	parser.add_option("--wait", action="store", type="float", dest="stall", help="wait at each step [seconds]")
	parser.add_option("--config",action="store", type="string", dest="fname", help="name of config file")
	parser.add_option("--simulate", action="store_true", dest="sim", default=False, help="simulate motor moves and bursting")
	parser.add_option("--checkbeam", action="store_true", dest="checkbeam", default=False, help="only acquire when beam is on")

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
	if options.detname == None:
#		detstr='XF:03IDA-BI{FS:1-CAM:1}'
		detstr=''
		print "must provide detector pv base, e.g., 'XF:28IDA-BI{URL:01}'"
		sys.exit()
	else:
		detstr=options.detname
	bmot = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.VAL')
	bmot_cur = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.RBV')
	bmot_stop = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}Mtr.STOP')
	umot = PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Inp:Pos')
	umot_cur = PV('SR:C5-ID:G1{IVU21:1-LEnc}Gap')
	umot_go = PV('SR:C5-ID:G1{IVU21:1-Mtr:2}Sw:Go')
	gmot = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.VAL')
	gmot_cur = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.RBV')
	gmot_stop = PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.STOP')
	traj_o_x=PV('SR:C31-{AI}Aie5-2:Offset-x-Cal')
	traj_o_y=PV('SR:C31-{AI}Aie5-2:Offset-y-Cal')
	traj_a_x=PV('SR:C31-{AI}Aie5-2:Angle-x-Cal')
	traj_a_y=PV('SR:C31-{AI}Aie5-2:Angle-y-Cal')
	shut_status=PV('SR:C05-EPS{PLC:1}Shutter:Sum-Sts')
	beam_current=PV('SR:C03-BI{DCCT:1}I:Total-I')
	bragg_temp=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:P}T-I')
	
	if detstr=='xf05bpm03' or detstr=='xf05bpm04':
		det0 = PV(detstr+':DataRead_Ch1')
		det1 = PV(detstr+':DataRead_Ch2')
		det2 = PV(detstr+':DataRead_Ch3')
		det3 = PV(detstr+':DataRead_Ch4')
	else:
		det0 = PV(detstr+'Cur:I0-I')
		det1 = PV(detstr+'Cur:I1-I')
		det2 = PV(detstr+'Cur:I2-I')
		det3 = PV(detstr+'Cur:I3-I')

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
	#check command line options
	if options.stall == None:
		twait = 0.
	else:
		twait = options.stall

#	display_list = np.zeros((pN+1,2))
#	count=0

	str='Start time is '+time.asctime()
	print str
	fp.write(str)
	fp.write('\n')
	if options.sim is True:
		str="      -----simulating motor moves and bursts-----"
		print str
		fp.write(str)
		fp.write('\n')
	str="Current position [mm]: %(XC)7.4f, %(YC)7.3f, %(ZC)7.3f" %\
	 {"XC":bmot_cur.get(),"YC":umot_cur.get(),"ZC":gmot_cur.get()}
	print str
	fp.write(str)
	fp.write('\n')
	time.sleep(2)
	LN=0
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
		try:
			ox=traj_o_x.get()
		except CA.Client.Exception:
			ox=12398
			continue
		try:
			oy=traj_o_y.get()
		except CA.Client.Exception:
			oy=12398
			continue
		try:
			ax=traj_a_x.get()
		except CA.Client.Exception:
			ax=12398
			continue
		try:
			ay=traj_a_y.get()
		except CA.Client.Exception:
			ay=12398
			continue
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
				time.sleep(60.)
			signal0=float(det0.get())
			signal1=float(det1.get())
			signal2=float(det2.get())
			signal3=float(det3.get())
			if signal0<1e-10:
				time.sleep(0.01)
				signal0=float(det0.get())
				signal1=float(det1.get())
				signal2=float(det2.get())
				signal3=float(det3.get())
		else:
			while ( options.checkbeam and (shut_open == False or beam_current == False)):
				print "Stopped.  Waiting for beam to return."
				time.sleep(60.)
			signal0=0.
			signal1=0.
			signal2=0.
			signal3=0.
		if options.sim is False:	
			str=' B= %(B)8.4f U= %(U)8.3f G= %(G)8.3f : %(C0)10.7e %(C1)10.7e %(C2)10.7e %(C3)10.7e TRAJ %(OX)6.3f %(OY)6.3f %(AX)6.3f %(AY)6.3f %(T)d'%{"B":float(bmot_cur.get()), "U":float(umot_cur.get()), "G":float(gmot_cur.get()), "C0":signal0, "C1":signal1, "C2":signal2, "C3":signal3, "OX":ox,"AX":ax,"OY":oy,"AY":ay, 'T':time.time()}
			print str
			fp.write(str)
			fp.write('\n')
		else:
			str=' B= %(B)8.4f U= %(U)8.3f G= %(G)8.3f : %(C0)10.7e %(C1)10.7e %(C2)10.7e %(C3)10.7e TRAJ %(OX)6.3f %(OY)6.3f %(AX)6.3f %(AY)6.3f'%{"B":tar[0][0], "U":tar[1][0], "G":tar[2][0], "C0":signal0, "C1":signal1, "C2":signal2, "C3":signal3, "OX":ox,"AX":ax,"OY":oy,"AY":ay} 
			print str
			fp.write(str)
			fp.write('\n')

#			display_list[count,0] = x
#			display_list[count,1] = signal0
#			count = count+1


	#return to starting positions
#	if options.sim is False:
#		bmot.put(float(angle[0]))
#		gmot.put(float(ivu[0]))
#		umot.put(float(t2gap[0]))
#		time.sleep(2)
#		xmot_stop.put(0)

	str='End time is '+time.asctime()
	print str
	fp.write(str)
	fp.write('\n')
	fp.close()

#	plt.figure()
#	plt.plot(display_list[:,0],display_list[:,1])
#	plt.plot(display_list[:,0],display_list[:,1],'go')
#	plt.show()
	return 0

if __name__ == "__main__":
	sys.exit(main())
