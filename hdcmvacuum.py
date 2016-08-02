# -*- coding: utf-8 -*-
"""
Created on Fri Apr  8 20:11:50 2016

@author: xf05id1
"""

from epics import PV
import time

fe = PV('XF:05ID-PPS{Sh:WB}Sts:Cls-Sts')
ringcurrent

dcmgv = PV('XF:05IDA-VA:1{Mono:HDCM-GV:1}Pos-Sts')

gv1down_open = PV('XF:05IDA-VA:1{Mono:HDCM-GV:1}Sts:FailOpn-Sts')
gv1up_open = PV('XF:05IDA-VA:1{Mir:1-GV:1}Sts:FailCls-Sts')
gv2up_open = PV('')

while True:
    if fe.get() is 1:
        if ringcurrent.get > 235 and   dcmgv.get() == 0:  
            gv1down_open.put(1)
            gv1up_open.put(1)
            gv2up_open.put(1)            
    time.sleep(60)
    