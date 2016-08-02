from __future__ import print_function
import epics
import math
import time

felist={#
 '5id1':{'ox':'SR:C31-{AI}Aie5-2:Offset-x-Cal', 'oy':'SR:C31-{AI}Aie5-2:Offset-y-Cal',\
 'ax':'SR:C31-{AI}Aie5-2:Angle-x-Cal', 'ay':'SR:C31-{AI}Aie5-2:Angle-y-Cal',\
 'bba8x':'SR:C05-BI{BPM:8}BbaXOff-SP', 'bba8y':'SR:C05-BI{BPM:8}BbaYOff-SP',\
 'bba9x':'SR:C05-BI{BPM:9}BbaXOff-SP', 'bba9y':'SR:C05-BI{BPM:9}BbaYOff-SP',\
 'ib':'FE:C05A-OP{Slt:3-Ax:I}Mtr.RBV', 'tb':'FE:C05A-OP{Slt:3-Ax:T}Mtr.RBV',\
 'ob':'FE:C05A-OP{Slt:4-Ax:O}Mtr.RBV', 'bb':'FE:C05A-OP{Slt:4-Ax:B}Mtr.RBV'\
 }
}
def moving(com,act,dbd):
	if math.fabs(math.fabs(com)-math.fabs(act))<float(dbd):
		return False 
	else:
		return True

class nsls2fe():
	def __init__(self,**kwargs):
		self.fe=epics.Device()
		self.fename='5id1'
		for name in felist[self.fename]:
			self.fe.add_pv(felist[self.fename][name])
	def AX(self):
		ax=None
		if felist[self.fename].has_key('ax'):
			try:
				ax=self.fe.PV(felist[self.fename]['ax']).get()
			except CA.Client.Exception:
				print("cannot connect to PV")
			else:
				return ax
		else:
			return None
	def AY(self):
		ay=None
		if felist[self.fename].has_key('ay'):
			try:
				ay=self.fe.PV(felist[self.fename]['ay']).get()
			except CA.Client.Exception:
				print("cannot connect to PV")
			else:
				return ay
		else:
			return None
	def OX(self):
		ox=None
		if felist[self.fename].has_key('ox'):
			try:
				ox=self.fe.PV(felist[self.fename]['ox']).get()
			except CA.Client.Exception:
				print("cannot connect to PV")
			else:
				return ox
		else:
			return None
	def OY(self):
		oy=None
		if felist[self.fename].has_key('oy'):
			try:
				oy=self.fe.PV(felist[self.fename]['oy']).get()
			except CA.Client.Exception:
				print("cannot connect to PV")
			else:
				return oy
		else:
			return None
	def BBA(self):
		self.bbalist={'bba8x':'','bba8y':'','bba9x':'','bba9y':''}
		for name in self.bbalist.keys():
			try:
				self.bbalist[name]=self.fe.PV(felist[self.fename][name]).get()
				#need this timeout...maybe the gate way?  no way to pass timeout to get()?
				time.sleep(0.1)
			except Exception:
				print("cannot connect to PV")
		return self.bbalist
	#todo: implement centers/gaps as in srxslit.py
	def tb(self,*args):
		pass
	def bb(self,*args):
		pass
	def ib(self,*args):
		pass
	def ob(self,*args):
		pass
	def hcen(self,*args):
		pass
	def vcen(self,*args):
		pass
	def hgap(self,*args):
		pass
	def vgap(self,*args):
		pass
