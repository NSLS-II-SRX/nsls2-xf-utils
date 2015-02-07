#! /usr/bin/env python
import sys
import time
import math
import string
import signal
from epics import PV
import numpy as np
import signal

def sigint_handler(signal,frame):
	print "Ctrl-C detected...exiting"
	sys.exit()
signal.signal(signal.SIGINT,sigint_handler)

#five samples, five time stamps, average power, average rate
ppow=np.array([[0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.],\
               [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.],
               [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.],
               [0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.,0.]])
#iterator array for the four gas detectors to keep track of running 5-pt avg
ppow_it=np.array([0,0,0,0])
#error check on the number of times the detectors have been polled
avgct=0
avgct1=0
avgct2=0
avgct3=0

#callbacks for updating gas detector stats
def cbf_u0(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
	#pass results to global storage
	global ppow
	global ppow_it
	global avgct
	#local temporary variables for calculating averages
	avg=0.
	tavg=0.
	ravg=0.
	#detect "pulse"
	if (value > 1e-11) and (value < 1):
		#save pulse power and time stamp
		ppow[0][ppow_it[0]]=value
		ppow[0][ppow_it[0]+5]=time.time()
		ppow_it[0]=int(math.fmod(ppow_it[0]+1,5))
		if avgct < 5:
			avgct=avgct+1
			for i in range(0,avgct):
				avg=avg+ppow[0][i]	
			if (ppow[0][4+avgct]-ppow[0][5])<=0:
				ppow[0][11]=0.
			else:
				ppow[0][11]=1./float(ppow[0][4+avgct]-ppow[0][5])*(avgct-1)
			ppow[0][10]=float(avg)/avgct
		else:
			for i in range(0,5):
				avg=avg+ppow[0][i]	
#			ppow[0][11]=1./math.fabs(ppow[0][9]-ppow[0][5])*4.
#			ppow[0][11]=1./math.fabs(ppow[0][ppow_it[0]]-ppow[0][tmp])*4.
			for i in range(2,5):
				tmp=int(math.fmod(ppow_it[0]+i,5))+5
				ravg=ravg+1./math.fabs(ppow[0][ppow_it[0]+5]-ppow[0][tmp])
			ppow[0][11]=ravg/3.
			ppow[0][10]=float(avg)/5.
def cbf_u1(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
	global ppow
	global ppow_it
	global avgct1
	avg=0.
	tavg=0.
	ravg=0.
	if (value > 1e-11) and (value < 1):
		ppow[1][ppow_it[1]]=value
		ppow[1][ppow_it[1]+5]=time.time()
		ppow_it[1]=int(math.fmod(ppow_it[1]+1,5))
		if avgct1 < 5:
			avgct1=avgct1+1
			for i in range(0,avgct1):
				avg=avg+ppow[1][i]	
			if (ppow[1][4+avgct1]-ppow[1][5])<=0:
				ppow[1][11]=0.
			else:
				ppow[1][11]=1./float(ppow[1][4+avgct1]-ppow[1][5])*(avgct1-1)
			ppow[1][10]=float(avg)/avgct1
		else:
			for i in range(0,5):
				avg=avg+ppow[1][i]	
			for i in range(2,5):
				tmp=int(math.fmod(ppow_it[1]+i,5))+5
				ravg=ravg+1./math.fabs(ppow[1][ppow_it[1]+5]-ppow[1][tmp])
			ppow[1][11]=ravg/3.
			ppow[1][10]=float(avg)/5.
def cbf_d0(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
	global ppow
	global ppow_it
	global avgct2
	avg=0.
	tavg=0.
	ravg=0.
	if (value > 1e-11) and (value < 1):
		ppow[2][ppow_it[2]]=value
		ppow[2][ppow_it[2]+5]=time.time()
		ppow_it[2]=int(math.fmod(ppow_it[2]+1,5))
		if avgct2 < 5:
			avgct2=avgct2+1
			for i in range(0,avgct2):
				avg=avg+ppow[2][i]	
			if (ppow[2][4+avgct2]-ppow[2][5])<=0:
				ppow[2][11]=0.
			else:
				ppow[2][11]=1./float(ppow[2][4+avgct2]-ppow[2][5])*(avgct2-1)
			ppow[2][10]=float(avg)/avgct2
		else:
			for i in range(0,5):
				avg=avg+ppow[2][i]	
			for i in range(2,5):
				tmp=int(math.fmod(ppow_it[2]+i,5))+5
				ravg=ravg+1./math.fabs(ppow[2][ppow_it[2]+5]-ppow[2][tmp])
			ppow[2][11]=ravg/3.
			ppow[2][10]=float(avg)/5.
def cbf_d1(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
	global ppow
	global ppow_it
	global avgct3
	avg=0.
	tavg=0.
	ravg=0.
	if (value > 1e-11) and (value < 1):
		ppow[3][ppow_it[3]]=value
		ppow[3][ppow_it[3]+5]=time.time()
		ppow_it[3]=int(math.fmod(ppow_it[3]+1,5))
		if avgct3 < 5:
			avgct3=avgct3+1
			for i in range(0,avgct3):
				avg=avg+ppow[3][i]	
			if (ppow[3][4+avgct3]-ppow[3][5])<=0:
				ppow[3][11]=0.
			else:
				ppow[3][11]=1./float(ppow[3][4+avgct3]-ppow[3][5])*(avgct3-1)
			ppow[3][10]=float(avg)/avgct3
		else:
			for i in range(0,5):
				avg=avg+ppow[3][i]	
			for i in range(2,5):
				tmp=int(math.fmod(ppow_it[3]+i,5))+5
				ravg=ravg+1./math.fabs(ppow[3][ppow_it[3]+5]-ppow[3][tmp])
			ppow[3][11]=ravg/3.
			ppow[3][10]=float(avg)/5.
#signal handler
def sigint_handler(signal,frame):
	print
	sys.exit()
signal.signal(signal.SIGINT,sigint_handler)

def main(argv=None):


	us_0_pv = PV('XF:05IDA{IM:1}Cur:I0-I')
	us_1_pv = PV('XF:05IDA{IM:1}Cur:I1-I')
	ds_0_pv = PV('XF:05IDA{IM:1}Cur:I2-I')
	ds_1_pv = PV('XF:05IDA{IM:1}Cur:I3-I')

	us_0_pv.add_callback(cbf_u0)
	us_0_pv.run_callbacks()
	us_1_pv.add_callback(cbf_u1)
	us_1_pv.run_callbacks()
	ds_0_pv.add_callback(cbf_d0)
	ds_0_pv.run_callbacks()
	ds_1_pv.add_callback(cbf_d1)
	ds_1_pv.run_callbacks()
	time.sleep(5)

	decu0=0
	decd0=0
	decu1=0
	decd1=0
	
	print " CH0\t\tCH1\t\tCH2\t\tCH3\t\tAvg\t\trun avg\t\t  Rate"
	while True:
		if ppow_it[0]==0:
			decu0=0
		else:
			decu0=1
#		if ((ppow[0][10]+ppow[1][10]+ppow[2][10]+ppow[3][10])/4.) > 2.:
#			fstr0='\033[40;91m'
#		elif ((ppow[0][10]+ppow[1][10]+ppow[2][10]+ppow[3][10])/4.) > 2.:
#			fstr0='\033[40;96m'
#		else:
#			fstr0='\033[40;94m'
#		fstr_term='\033[0m'
		fstr0=fstr_term=''
		sys.stdout.write("%(pow1)8.6e  %(pow2)8.6e  %(pow3)8.6e  %(pow4)8.6e   %(FSS)s%(gavg)8.6e \t\t%(Tavg)8.6e%(FST)s\t%(rate)06.2f Hz\r"%{'pow1':ppow[0][ppow_it[0]-decu0],'pow2':ppow[1][ppow_it[1]-decu1],'pow3':ppow[2][ppow_it[2]-decd0],'pow4':ppow[3][ppow_it[3]-decd1],'gavg':(ppow[0][ppow_it[0]-decu0]+ppow[1][ppow_it[1]-decu1]+ppow[2][ppow_it[2]-decd0]+ppow[3][ppow_it[3]-decd1])/4.,'Tavg':(ppow[0][10]+ppow[1][10]+ppow[2][10]+ppow[3][10])/4.,'rate':(ppow[0][11]+ppow[1][11]+ppow[2][11]+ppow[3][11])/4./.6/.6, 'FSS':fstr0, 'FST':fstr_term})		
		sys.stdout.flush()
		time.sleep(.01)
	return 0

if __name__ == "__main__":
	sys.exit(main())

