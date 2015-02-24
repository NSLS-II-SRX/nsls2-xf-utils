import epics
import math
import time

bpmlist={#
 'bpm1':{'Xr':'XF:05IDA-BI:1{BPM:1-Ax:XDiode}Mtr.RBV','Xc':'XF:05IDA-BI:1{BPM:1-Ax:XDiode}Mtr.VAL',\
  'Yr':'XF:05IDA-BI:1{BPM:1-Ax:YDiode}Mtr.RBV','Yc':'XF:05IDA-BI:1{BPM:1-Ax:YDiode}Mtr.VAL',\
  'D0':'xf05bpm03:DataRead_Ch1','D1':'xf05bpm03:DataRead_Ch2','D2':'xf05bpm03:DataRead_Ch3',\
  'D3':'xf05bpm03:DataRead_Ch4', 'Da':'xf05bpm03:Acq', 'Fr':'XF:05IDA-BI:1{BPM:1-Ax:YFoil}Mtr.RBV',\
  'Fc':'XF:05IDA-BI:1{BPM:1-Ax:YFoil}Mtr.VAL'},\
 'bpm2':{'Xr':'XF:05IDB-BI:1{BPM:2-Ax:XDiode}Mtr.RBV','Xc':'XF:05IDB-BI:1{BPM:2-Ax:XDiode}Mtr.VAL',\
  'Yr':'XF:05IDB-BI:1{BPM:2-Ax:YDiode}Mtr.RBV','Yc':'XF:05IDB-BI:1{BPM:2-Ax:YDiode}Mtr.VAL',\
  'D0':'xf05bpm04:DataRead_Ch1','D1':'xf05bpm04:DataRead_Ch2','D2':'xf05bpm04:DataRead_Ch3',\
  'D3':'xf05bpm04:DataRead_Ch4', 'Da':'xf05bpm04:Acq', 'Fr':'XF:05IDB-BI:1{BPM:2-Ax:YFoil}Mtr.RBV',\
  'Fc':'XF:05IDB-BI:1{BPM:2-Ax:YFoil}Mtr.VAL'}\
}

def moving(com,act,dbd):
	if math.fabs(math.fabs(com)-math.fabs(act))<float(dbd):
		return False 
	else:
		return True

class nsls2bpm():
	def __init__(self,**kwargs):
		self.bpm=epics.Device()
		self.bpmname=None
		if kwargs.has_key('bpm'):
			if kwargs['bpm'].lower()=='bpm1':
				self.bpmname='bpm1'
				for name in bpmlist['bpm1']:
					self.bpm.add_pv(bpmlist['bpm1'][name])
			elif kwargs['bpm'].lower()=='bpm2':
				self.bpmname='bpm2'
				for name in bpmlist['bpm2']:
					self.bpm.add_pv(bpmlist['bpm2'][name])
			else:
				print "Don't recognize this BPM...exiting."		
				return None
		else:
			return None
	def diode0(self):
		d0=None
		if bpmlist[self.bpmname].has_key('D0'):
			try:
				d0=self.bpm.PV(bpmlist[self.bpmname]['D0']).get()
			except CA.Client.Exception:
				print "cannot connect to PV"
			else:
				return d0
		else:
			return None
	def diode1(self):
		d1=None
		if bpmlist[self.bpmname].has_key('D1'):
			try:
				d1=self.bpm.PV(bpmlist[self.bpmname]['D1']).get()
			except CA.Client.Exception:
				print "cannot connect to PV"
			else:
				return d1
		else:
			return None
	def diode2(self):
		d2=None
		if bpmlist[self.bpmname].has_key('D2'):
			try:
				d2=self.bpm.PV(bpmlist[self.bpmname]['D2']).get()
			except CA.Client.Exception:
				print "cannot connect to PV"
			else:
				return d2
		else:
			return None
	def diode3(self):
		d3=None
		if bpmlist[self.bpmname].has_key('D3'):
			try:
				d3=self.bpm.PV(bpmlist[self.bpmname]['D3']).get()
			except CA.Client.Exception:
				print "cannot connect to PV"
			else:
				return d3
		else:
			return None
	def H(self):
		H=None
		d1=self.diode1()
		while d1==0.:
			d1=self.diode1()
		d3=self.diode3()
		while d3==0.:
			d3=self.diode3()
		if d1 is not None and d3 is not None:
			H=(d3-d1)/(d3+d1)
			return H
		else:
			return None
	def V(self):
		V=None
		d0=self.diode0()
		d2=self.diode2()
		if d0 is not None and d2 is not None:
			V=(d0-d2)/(d0+d2)
			return V
		else:
			return None
	def X(self,*args):
		if len(args)==0:
			return self.bpm.PV(bpmlist[self.bpmname]['Xr']).get()
		else:
			self.bpm.PV(bpmlist[self.bpmname]['Xc']).put(float(args[0]))
			while moving(self.bpm.PV(bpmlist[self.bpmname]['Xr']).get(),float(args[0]),0.001) is True:
				time.sleep(0.1)
			return self.bpm.PV(bpmlist[self.bpmname]['Xr']).get()
	def Y(self,*args):
		if len(args)==0:
			return self.bpm.PV(bpmlist[self.bpmname]['Yr']).get()
		else:
			self.bpm.PV(bpmlist[self.bpmname]['Yc']).put(float(args[0]))
			while moving(self.bpm.PV(bpmlist[self.bpmname]['Yr']).get(),float(args[0]),0.001) is True:
				time.sleep(0.1)
			return self.bpm.PV(bpmlist[self.bpmname]['Yr']).get()
	def acq(self):
		#sometimes the tetramm hangs, but reports good status via acq pb
		#sometimes, when it's self an acq stop followed by an acq start, it returns garbage
		#the wait attempts to ameliorate this latter behavior
		if self.bpm.PV(bpmlist[self.bpmname]['Da']).get()==1:
			self.bpm.PV(bpmlist[self.bpmname]['Da']).put(0)
			time.sleep(0.5)
		self.bpm.PV(bpmlist[self.bpmname]['Da']).put(1)
	def foil(self,*args):
		#todo: report which detector/foil is in at readback position via dict
		if len(args)==0:
			return self.bpm.PV(bpmlist[self.bpmname]['Fr']).get()
		else:
			self.bpm.PV(bpmlist[self.bpmname]['Fc']).put(float(args[0]))
			while moving(self.bpm.PV(bpmlist[self.bpmname]['Fr']).get(),float(args[0]),0.001) is True:
				time.sleep(0.1)
			return self.bpm.PV(bpmlist[self.bpmname]['Fr']).get()

