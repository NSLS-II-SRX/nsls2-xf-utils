from __future__ import print_function
import sys
from epics import PV
from epics import poll
import math
import time
import numpy as np


class mottwin():
    def __init__(self,**kwargs):
        try:
            self._m1val=PV(kwargs['m1']+'.VAL')
            self._m1rbv=PV(kwargs['m1']+'.RBV')
        except KeyError:
            return 'm1 key not found in declaration'
        try:
            self._m2val=PV(kwargs['m2']+'.VAL')
            self._m2rbv=PV(kwargs['m2']+'.RBV')
        except KeyError:
            return 'm2 key not found in declaration'
        #by default the two motors are referenced to their own zero,
        #provide keyword offset if this is not true
        #semantic meaning:  m2 dial is offset by kwargs['offset'] from m1 dial
        if 'offset' in kwargs:
        # if kwargs.has_key('offset'):
            self.__m2m1off=float(kwargs['offset'])
        else:
            self.__m2m1off=0.097
        #define incremental step size in engineering units
        self.__stepsize=0.001
        #define software deadband
        # if kwargs.has_key('deadband'):
        if 'deadband' in kwargs:
            self.__dbd=float(kwargs['deadband'])
        else:
            self.__dbd=0.005

    def _indeadband(self,com,act,dbd):
        if math.fabs(com-act)<float(dbd):
            return True 
        else:
            return False

    def mov(self,*args):
        """absolute pseudo motor move
        > object.mov(0.0)
        """
        if len(args) is not 1:
            raise SyntaxError
        #target positions for motors
        m1tar=float(args[0])
        m2tar=float(args[0])+self.__m2m1off
        #calculate trajectories for motors based on self.__stepsize
        m1cur=float(self._m1rbv.get())
        m2cur=float(self._m2rbv.get())
        nsteps=abs(int(np.round((m1tar-self._m1rbv.get())/self.__stepsize,0)))
        m1traj=np.linspace(self._m1rbv.get(),m1tar,nsteps)
        m2traj=np.linspace(self._m2rbv.get(),m2tar,nsteps)
        print("\ttarget\t\tm1\t\tm2\n")
        for i in range(0,nsteps):
            self._m1val.put(m1traj[i])
            self._m2val.put(m2traj[i])
            time.sleep(0.05)
            while( self._indeadband(self._m1rbv.get(),m1traj[i],self.__dbd) is False or
             self._indeadband(self._m2rbv.get(),m2traj[i],self.__dbd) is False):
                time.sleep(0.050)
                self._m1val.put(m1traj[i])
                self._m2val.put(m2traj[i])
            if i%5 == 0:
                outstr='\r\t%(tar)10.6f\t%(m1)10.6f\t%(m2)10.6f'%{'tar':m1traj[i],\
                 'm1':self._m1rbv.get(),'m2':self._m2rbv.get()}
                sys.stdout.write(outstr)
                sys.stdout.flush()
        outstr='\r\t%(tar)10.6f\t%(m1)10.6f\t%(m2)10.6f'%{'tar':m1tar,\
         'm1':float(self._m1rbv.get()),'m2':float(self._m2rbv.get())}
        sys.stdout.write(outstr)
        sys.stdout.flush()

    def movr(self,*args):
        """relative pseudo motor move
        > object.rmov(0.01)
        """
        if len(args) is not 1:
            raise SyntaxError
        #target positions for motors
        m1tar=float(args[0]+self._m1rbv.get())
        self.mov(m1tar)

    def wh(self):
        """query physical motor positions
        """
        print("%(m1)s\t%(m2)s"%{'m1':self._m1rbv.pvname,'m2':self._m2rbv.pvname})
        print('%(m1)10.6f\t\t\t\t%(m2)10.6f'%\
         {'m1':float(self._m1rbv.get()),'m2':float(self._m2rbv.get())})


