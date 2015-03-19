from epics import PV
from epics import poll
import math
import time

#updated the SSA closed positions on 2015/3/2, ycchen

def moving(com,act,dbd):
	if math.fabs(math.fabs(com)-math.fabs(act))<float(dbd):
		return False 
	else:
		return True

class nsls2slit():
	def __init__(self,**kwargs):
		#need to identify slit and set zero positions
		#if a slit has a horizontal component, its 
		#offsets should be here
		if kwargs.__contains__('ib'):
			#check for Slit 1
			if (kwargs['ib'].split(':')[1][:5]=='05IDA') and\
			 (kwargs['ib'].split('{')[1][:5]=='Slt:1'):	
				self.BB0=-5.63
				self.IB0=-6.610
				self.OB0=-4.430
				self.TB0=-5.70
#				print "This is SRX's white beam slit."
				self._slitctrlr='pmac'
			elif (kwargs['ib'].split(':')[1][:5]=='05IDA') and\
			 (kwargs['ib'].split('{')[1][:5]=='Slt:2'):
				self.BB0=0.
				self.IB0=-6.535
				self.OB0=-5.065
				self.TB0=0.
				self._slitctrlr='pmac'
#				print "This is SRX's first pink beam slit."
			elif (kwargs['ib'].split(':')[1][:5]=='05IDB') and\
			 (kwargs['ib'].split('{')[1][:7]=='Slt:SSA'):
			#	self.BB0=-3.6
			#	self.IB0=-1.2
			#	self.OB0=-3.8
			#	self.TB0=-0.7

                       		self.BB0=-2.405
                                self.IB0=-0.0305
                                self.OB0=0.9
                                self.TB0=0.44
				self._slitctrlr='smaract'

#				print "This is SRX's secondary source aperture."
			else:
				self.BB0=0.
				self.IB0=0.
				self.OB0=0.
				self.TB0=0.
				self._slitctrlr='generic'
				print "unknown slit, offsets assumed to be zero"
		#if it is purely a vertical slit it should be here
		elif kwargs.__contains__('bb'):
			self.BB0=0.
			self.IB0=0.
			self.OB0=0.
			self.TB0=0.
			print "unknown slit, offsets assumed to be zero"
			self._slitctrlr='generic'
		else:
			print "Cannot identify slit"
			return None	
		
		if kwargs.has_key('ib'):
			self.ibr=PV(kwargs['ib']+'Mtr.RBV')
			self.ibp=PV(kwargs['ib']+'Mtr.VAL')
			self.ISLIT=True
		else:
			self.ISLIT=False
		if kwargs.has_key('ob'):
			self.obr=PV(kwargs['ob']+'Mtr.RBV')
			self.obp=PV(kwargs['ob']+'Mtr.VAL')
			self.OSLIT=True
		else:
			self.OSLIT=False
		if kwargs.has_key('tb'):
			self.tbr=PV(kwargs['tb']+'Mtr.RBV')
			self.tbp=PV(kwargs['tb']+'Mtr.VAL')
			self.TSLIT=True
		else:
			self.TSLIT=False
		if kwargs.has_key('bb'):
			self.bbr=PV(kwargs['bb']+'Mtr.RBV')
			self.bbp=PV(kwargs['bb']+'Mtr.VAL')
			self.BSLIT=True
		else:
			self.BSLIT=False
		if self.ISLIT is True and self.OSLIT is True:
			self.HSLIT=True
		else:
			self.HSLIT=False
		if self.BSLIT is True and self.TSLIT is True:
			self.VSLIT=True
		else:
			self.VSLIT=False
	@property
	def slitctrlr(self):
		return self._slitctrlr
	def hcen(self,*args):
		if self.HSLIT is not True:
			print "Horizontal slit blades not defined."
			return None
		ip=self.ibr.get()-self.IB0
		op=self.obr.get()-self.OB0
		zp=(op-ip)/2.
		if len(args)==0:
			return zp
		else:
			ip=self.IB0-args[0]+self.hsize()/2.
			op=self.OB0+args[0]+self.hsize()/2.
			if self._slitctrlr=='smaract':
				if (args[0] < zp):
					self.ibp.put(ip)
					self.obp.put(op)
				else:
					self.obp.put(op)
					self.ibp.put(ip)
			else:
				self.ibp.put(ip)
				self.obp.put(op)
			while moving(self.ibr.get(),ip,0.002) or moving(self.obr.get(),op,0.002):
				time.sleep(0.01)
	def vcen(self,*args):
		if self.VSLIT is not True:
			print "Vertical slit blades not defined."
			return None
		bp=self.bbr.get()-self.BB0
		tp=self.tbr.get()-self.TB0
		zp=(tp-bp)/2.
		if len(args)==0:
			return zp
		else:
			tp=self.TB0+args[0]+self.vsize()/2.
			bp=self.BB0-args[0]+self.vsize()/2.
			if self._slitctrlr=='smaract':
				if (args[0] < zp):
					self.bbp.put(bp)
					self.tbp.put(tp)
				else:
					self.tbp.put(tp)
					self.bbp.put(bp)
			else:
				self.tbp.put(tp)
				self.bbp.put(bp)
			while moving(self.tbr.get(),tp,0.002) or moving(self.bbr.get(),bp,0.002):
				time.sleep(0.01)
			return self.vcen()
	def hsize(self,*args):
		if self.HSLIT is not True:
			print "Horizontal slit blades not defined."
			return None
		if len(args)==0:
			ip=self.ibr.get()-self.IB0
			op=self.obr.get()-self.OB0
			gap=(ip+op)
			return gap
		else:
			hc=self.hcen()
			if hc<0.:
				ip=self.IB0+args[0]/2.-hc
				op=self.OB0+args[0]/2.+hc
			else:
				ip=self.IB0+args[0]/2.-hc
				op=self.OB0+args[0]/2.+hc
			self.ibp.put(ip)
			self.obp.put(op)
			while moving(self.ibr.get(),ip,0.002) or moving(self.obr.get(),op,0.002):
				time.sleep(0.01)
			ip=self.ibr.get()-self.IB0
			op=self.obr.get()-self.OB0
			gap=(ip+op)
			return gap
	def vsize(self,*args):
		if self.VSLIT is not True:
			print "Vertical slit blades not defined."
			return None
		bp=self.bbr.get()-self.BB0
		tp=self.tbr.get()-self.TB0
		gap=(bp+tp)
		if len(args)==0:
			return gap
		else:
			vc=self.vcen()
			if vc<0.:
				bp=self.BB0+args[0]/2.-vc
				tp=self.TB0+args[0]/2.+vc
			else:
				bp=self.BB0+args[0]/2.-vc
				tp=self.TB0+args[0]/2.+vc
			self.bbp.put(bp)
			self.tbp.put(tp)
			while moving(self.tbr.get(),tp,0.002) or moving(self.bbr.get(),bp,0.002):
				time.sleep(0.01)
			bp=self.bbr.get()-self.BB0
			tp=self.tbr.get()-self.TB0
			gap=(bp+tp)
			return gap
	def ibraw(self,*args):
		if self.HSLIT is not True:
			print "Horizontal slit blades not defined."
			return None
		if len(args)==0:
			ip=self.ibr.get()
			return ip
		else:
			ip=args[0]
			self.ibp.put(ip)
			while moving(self.ibr.get(),ip,0.002):
				time.sleep(0.01)
			ip=self.ibr.get()
			return ip
	def obraw(self,*args):
		if self.HSLIT is not True:
			print "Horizontal slit blades not defined."
			return None
		if len(args)==0:
			op=self.obr.get()
			return op
		else:
			op=args[0]
			self.obp.put(op)
			while moving(self.obr.get(),op,0.002):
				time.sleep(0.01)
			op=self.obr.get()
			return op
	def tbraw(self,*args):
		if self.VSLIT is not True:
			print "Vertical slit blades not defined."
			return None
		if len(args)==0:
			tp=self.tbr.get()
			return tp
		else:
			tp=args[0]
			self.tbp.put(tp)
			while moving(self.tbr.get(),tp,0.002):
				time.sleep(0.01)
			tp=self.tbr.get()
			return tp
	def bbraw(self,*args):
		if self.VSLIT is not True:
			print "Vertical slit blades not defined."
			return None
		if len(args)==0:
			bp=self.bbr.get()
			return bp
		else:
			bp=args[0]
			self.bbp.put(bp)
			while moving(self.bbr.get(),bp,0.002):
				time.sleep(0.01)
			bp=self.bbr.get()
			return bp
