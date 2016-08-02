from __future__ import print_function
from epics import PV
from epics import poll
import math
import time

#updated the SSA closed positions on 2015/3/2, ycchen
#updated the SSA closed positions on 2015/4/11 for 24 mm Xoffset, C1R=-5.021, ycchen

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
                self._BB0=-4.905
                #self._BB0=-4.855               
                self._IB0=-6.705
                #self._IB0=-6.585               
                self._OB0=-4.345
                #self._OB0=-4.465
                self._TB0=-5.775
                #self._TB0=-5.825
#               print("This is SRX's white beam slit.")
                self._slitctrlr='pmac'
            elif (kwargs['ib'].split(':')[1][:5]=='05IDA') and\
             (kwargs['ib'].split('{')[1][:5]=='Slt:2'):
                self._BB0=0.
                self._IB0=-6.535
                self._OB0=-5.065
                self._TB0=0.
                self._slitctrlr='pmac'
#               print("This is SRX's first pink beam slit.")
            elif (kwargs['ib'].split(':')[1][:5]=='05IDB') and\
             (kwargs['ib'].split('{')[1][:7]=='Slt:SSA'):
            #   self._BB0=-3.6
            #   self._IB0=-1.2
            #   self._OB0=-3.8
            #   self._TB0=-0.7
           #    self._BB0=-2.405
           #    self._IB0=-0.0305
           #    self._OB0=0.9
           #    self._TB0=0.44
           #inboard and outboard closed position for xoffset = 24 mm, C1R = -5.021, 12.5keV
                self._BB0=-2.2046
                #self._IB0=0.4005
                #self._OB0=0.4710
                self._IB0=-0.4895
                self._OB0=1.3610
                self._TB0=0.2396
                self._slitctrlr='smaract'

#               print("This is SRX's secondary source aperture.")
            elif (kwargs['ib'].split(':')[2]=='34-Ax'):
                self._BB0=0.
                self._IB0=0.
                self._OB0=0.
                self._TB0=0.
                self._slitctrlr='softioc'
            else:
                self._BB0=0.
                self._IB0=0.
                self._OB0=0.
                self._TB0=0.
                self._slitctrlr='generic'
                print("unknown slit, offsets assumed to be zero")
        #if it is purely a vertical slit it should be here
        elif kwargs.__contains__('bb'):
            self._BB0=0.
            self._IB0=0.
            self._OB0=0.
            self._TB0=0.
            print("unknown slit, offsets assumed to be zero")
            self._slitctrlr='generic'
        else:
            print("Cannot identify slit")
            return None 
        
        if 'ib' in kwargs:
            self.ibr=PV(kwargs['ib']+'Mtr.RBV')
            self.ibp=PV(kwargs['ib']+'Mtr.VAL')
            self.__ISLIT=True
        else:
            self.__ISLIT=False
        if 'ob' in kwargs:
            self.obr=PV(kwargs['ob']+'Mtr.RBV')
            self.obp=PV(kwargs['ob']+'Mtr.VAL')
            self.__OSLIT=True
        else:
            self.__OSLIT=False
        if 'tb' in kwargs:
            self.tbr=PV(kwargs['tb']+'Mtr.RBV')
            self.tbp=PV(kwargs['tb']+'Mtr.VAL')
            self.__TSLIT=True
        else:
            self.__TSLIT=False
        if 'bb' in kwargs:
            self.bbr=PV(kwargs['bb']+'Mtr.RBV')
            self.bbp=PV(kwargs['bb']+'Mtr.VAL')
            self.__BSLIT=True
        else:
            self.__BSLIT=False
        if self.__ISLIT is True and self.__OSLIT is True:
            self.__HSLIT=True
        else:
            self.__HSLIT=False
        if self.__BSLIT is True and self.__TSLIT is True:
            self.__VSLIT=True
        else:
            self.__VSLIT=False
    @property
    def slitctrlr(self):
        return self._slitctrlr
    def hcen(self,*args):
        if self.__HSLIT is not True:
            print("Horizontal slit blades not defined.")
            return None
        ip=self.ibr.get()-self._IB0
        op=self.obr.get()-self._OB0
        zp=(op-ip)/2.
        if len(args)==0:
            return zp
        else:
            ip=self._IB0-args[0]+self.hsize()/2.
            op=self._OB0+args[0]+self.hsize()/2.
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
        if self.__VSLIT is not True:
            print("Vertical slit blades not defined.")
            return None
        bp=self.bbr.get()-self._BB0
        tp=self.tbr.get()-self._TB0
        zp=(tp-bp)/2.
        if len(args)==0:
            return zp
        else:
            tp=self._TB0+args[0]+self.vsize()/2.
            bp=self._BB0-args[0]+self.vsize()/2.
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
        if self.__HSLIT is not True:
            print("Horizontal slit blades not defined.")
            return None
        if len(args)==0:
            ip=self.ibr.get()-self._IB0
            op=self.obr.get()-self._OB0
            gap=(ip+op)
            return gap
        else:
            hc=self.hcen()
            if hc<0.:
                ip=self._IB0+args[0]/2.-hc
                op=self._OB0+args[0]/2.+hc
            else:
                ip=self._IB0+args[0]/2.-hc
                op=self._OB0+args[0]/2.+hc
            self.ibp.put(ip)
            self.obp.put(op)
            while moving(self.ibr.get(),ip,0.002) or moving(self.obr.get(),op,0.002):
                time.sleep(0.01)
            ip=self.ibr.get()-self._IB0
            op=self.obr.get()-self._OB0
            gap=(ip+op)
            return gap
    def vsize(self,*args):
        if self.__VSLIT is not True:
            print("Vertical slit blades not defined.")
            return None
        bp=self.bbr.get()-self._BB0
        tp=self.tbr.get()-self._TB0
        gap=(bp+tp)
        if len(args)==0:
            return gap
        else:
            vc=self.vcen()
            if vc<0.:
                bp=self._BB0+args[0]/2.-vc
                tp=self._TB0+args[0]/2.+vc
            else:
                bp=self._BB0+args[0]/2.-vc
                tp=self._TB0+args[0]/2.+vc
            self.bbp.put(bp)
            self.tbp.put(tp)
            while moving(self.tbr.get(),tp,0.002) or moving(self.bbr.get(),bp,0.002):
                time.sleep(0.01)
            bp=self.bbr.get()-self._BB0
            tp=self.tbr.get()-self._TB0
            gap=(bp+tp)
            return gap
    def ibraw(self,*args):
        if self.__HSLIT is not True:
            print("Horizontal slit blades not defined.")
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
        if self.__HSLIT is not True:
            print("Horizontal slit blades not defined.")
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
        if self.__VSLIT is not True:
            print("Vertical slit blades not defined.")
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
        if self.__VSLIT is not True:
            print("Vertical slit blades not defined.")
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
