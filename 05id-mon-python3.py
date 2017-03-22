#! /opt/conda_envs/collection/bin/python 
import os
import epics
import numpy
import sys
import time
import signal
from colorclass import Color as col
import terminaltables
import tempdev
from optparse import OptionParser


#global variables
global gvalarm
global ccgalarm
global gvlist
global ccglist
global igvlist
global iccglist
global flowlist
global iflowlist
global flowalarm
global pending_update
global tobj
tobj=tempdev.EPSTemperature()
ok_str=col('{autoblue}OK{/autoblue}')
ee_str=col('{autored}EE{/autored}')
ww_str=col('{autoyellow}WW{/autoyellow}')
def oktext(s):
    return col('{autoblue}%s{/autoblue}'%s)
def wwtext(s):
    return col('{autoyellow}%s{/autoyellow}'%s)
def eetext(s):
    return col('{autored}%s{/autored}'%s)
#dict for beamline gate valves
gvlist={'00 GV_MASK':'FE:C05A-VA{GV:2}DB:Pos-Sts',\
 '03 GV_BC2':'XF:05IDA-VA:1{BT:1-GV:1}Pos-Sts',\
 '04 GV_HFM':'XF:05IDA-VA:1{Slt:1-GV:1}Pos-Sts',\
 '05 GV_DCM':'XF:05IDA-VA:1{Mir:1-GV:1}Pos-Sts',\
 '06 GV_BPM1':'XF:05IDA-VA:1{Mono:HDCM-GV:1}Pos-Sts',\
 '07 GV_SH-A':'XF:05IDA-VA:1{BPM:1-GV:1}Pos-Sts',\
 '09 GV_BPM2':'XF:05IDB-VA:1{BT:1-GV:1}Pos-Sts',\
 '10 GV_SH-B':'XF:05IDB-VA:1{Slt:SSA-GV:1}Pos-Sts',\
 '13 GV_HFFM':'XF:05IDD-VA:1{BT:1-GV:1}Pos-Sts'\
}
#inverse dictionary
#translates PV to key
igvlist=dict((gvlist[j],j) for j in gvlist.keys())
#dict for CCGs
#'key',['PV',warn limit, alarm limit]
ccglist={'00 IG_MASK':['XF:05IDA-VA:0{Msk:1-CCG:1}P-I',5e-9,1e-8],\
 '01 IG_BC1':['XF:05IDA-VA:0{BC:1-CCG:1}P-I',8e-9,5e-8],\
 '03 IG_BC2':['XF:05IDA-VA:1{BC:2-CCG:1}P-I',8e-9,5e-8],\
 '04 IG_HFM':['XF:05IDA-VA:1{Mir:1-CCG:1}P-I',3e-8,5e-8],\
 '05 IG_DCM':['XF:05IDA-VA:1{Mono:HDCM-CCG:1}P-I',1e-7,4e-7],\
 '06 IG_BPM1':['XF:05IDA-VA:1{BPM:1-CCG:1}P-I',8e-9,5e-8],\
 '07 IG_SH-A':['XF:05IDA-VA:1{PSh:2-CCG:1}P-I',8e-9,5e-8],\
 '08 IG_BT-B':['XF:05IDB-VA:1{BT:1-CCG:1}P-I',8e-9,5e-8],\
 '09 IG_BPM2':['XF:05IDB-VA:1{BPM:2-CCG:1}P-I',5e-8,1e-7],\
 '10 IG_SH-B':['XF:05IDB-VA:1{PSh:4-CCG:1}P-I',8e-9,3e-8],\
 '11 IG_BT-C':['XF:05IDD-VA:1{BT:1-CCG:1}P-I',8e-9,3e-8],\
 '12 IG_BT-D':['XF:05IDD-VA:1{BT:1-CCG:2}P-I',8e-9,1e-8],\
 '13 IG_HFFM':['XF:05IDD-VA:1{Mir:2-CCG:1}P-I',3e-8,5e-8],\
 '14 IG_HRFM':['XF:05IDD-VA:1{Mir:4-CCG:1}P-I',3e-8,5e-8]\
}
iccglist=dict((ccglist[j][0],j) for j in ccglist.keys())
flowlist={'00 FL_MASK':['XF:05IDA-OP:1{Msk:1}F-1-I',1.1,1.],\
 '01 FL_BC1':['XF:05IDA-OP:1{Fltr:1}F-I',1.0,.8],\
 '02 FL_BT-A':['XF:05IDA-OP:1{Slt:1}F-I',1.,.8],\
 '03 FL_BC2':['XF:05IDA-OP:1{Mir:1}F-I',.83,.75],\
 '04 FL_HFM':['XF:05IDA-OP:1{Slt:2}F-I',.9,.8],\
 '05 FL_DCM':['XF:05IDA-OP:1{Mono:HDCM}F-I',.88,.8],\
 '06 FL_BPM1':['XF:05IDA-OP:1{BS:WB}F-1-I',.93,.85]\
}
iflowlist=dict((flowlist[j][0],j) for j in flowlist.keys())
#high voltage power supplies for ion pumps
hvlist={'00 HV_MASK':'XF:05IDA-VA:0{Msk:1-IP:1}Err:Supply-Sts',\
 '01 HV_BC1':'XF:05IDA-VA:0{BC:1-IP:1}Err:Supply-Sts',\
 '02 HV_BT-A':'XF:05IDA-VA:1{BT:1-IP:1}Err:Supply-Sts',\
 '03 HV_BC2':'XF:05IDA-VA:1{BC:2-IP:1}Err:Supply-Sts',\
 '04 HV_HFM':'XF:05IDA-VA:1{Mir:1-IP:1}Err:Supply-Sts',\
 '05 HV_DCM':'XF:05IDA-VA:1{Mono:HDCM-IP:1}Err:Supply-Sts',\
 '06 HV_BPM1':'XF:05IDA-VA:1{BPM:1-IP:1}Err:Supply-Sts',\
 '07 HV_SH-A':'XF:05IDA-VA:1{PSh:2-IP:1}Err:Supply-Sts',\
 '08 HV_BT-B':'XF:05IDB-VA:1{BT:1-IP:1}Err:Supply-Sts',\
 '09 HV_BPM2':'XF:05IDB-VA:1{BPM:2-IP:1}Err:Supply-Sts',\
 '10 HV_SH-B':'XF:05IDB-VA:1{PSh:4-IP:1}Err:Supply-Sts',\
 '11 HV_BT-C':'XF:05IDD-VA:1{BT:1-IP:1}Err:Supply-Sts',\
 '12 HV_BT-D':'XF:05IDD-VA:1{BT:1-IP:2}Err:Supply-Sts',\
 '13 HV_HFFM':'XF:05IDD-VA:1{Mir:2-IP:1}Err:Supply-Sts',\
 '14 HV_HRFM':'XF:05IDD-VA:1{Mir:4-IP:1}Err:Supply-Sts'\
}
ihvlist=dict((hvlist[j],j) for j in hvlist.keys())
#dict for error status
errlist={'00 MASK':'FE:C05A-VA{GV:2}DB:Pos-Sts',\
 '03 GV_BC2':'XF:05IDA-VA:1{BT:1-GV:1}Err-Sts',\
 '04 GV_HFM':'XF:05IDA-VA:1{Slt:1-GV:1}Err-Sts',\
 '05 GV_DCM':'XF:05IDA-VA:1{Mir:1-GV:1}Err-Sts',\
 '06 GV_BPM1':'XF:05IDA-VA:1{Mono:HDCM-GV:1}Err-Sts',\
 '07 GV_SH-A':'XF:05IDA-VA:1{BPM:1-GV:1}Err-Sts',\
 '09 GV_BPM2':'XF:05IDB-VA:1{BT:1-GV:1}Err-Sts',\
 '10 GV_SH-B':'XF:05IDB-VA:1{Slt:SSA-GV:1}Err-Sts',\
 '13 GV_HFFM':'XF:05IDD-VA:1{BT:1-GV:1}Err-Sts',\
 '00 IG_MASK':'XF:05IDA-VA:0{Msk:1-CCG:1}P-Sts',\
 '01 IG_BC1':'XF:05IDA-VA:0{BC:1-CCG:1}P-Sts',\
 '03 IG_BC2':'XF:05IDA-VA:1{BC:2-CCG:1}P-Sts',\
 '04 IG_HFM':'XF:05IDA-VA:1{Mir:1-CCG:1}P-Sts',\
 '05 IG_DCM':'XF:05IDA-VA:1{Mono:HDCM-CCG:1}P-Sts',\
 '06 IG_BPM1':'XF:05IDA-VA:1{BPM:1-CCG:1}P-Sts',\
 '07 IG_SH-A':'XF:05IDA-VA:1{PSh:2-CCG:1}P-Sts',\
 '08 IG_BT-B':'XF:05IDB-VA:1{BT:1-CCG:1}P-Sts',\
 '09 IG_BPM2':'XF:05IDB-VA:1{BPM:2-CCG:1}P-Sts',\
 '10 IG_SH-B':'XF:05IDB-VA:1{PSh:4-CCG:1}P-Sts',\
 '11 IG_BT-C':'XF:05IDD-VA:1{BT:1-CCG:1}P-Sts',\
 '12 IG_BT-D':'XF:05IDD-VA:1{BT:1-CCG:2}P-Sts',\
 '13 IG_HFFM':'XF:05IDD-VA:1{Mir:2-CCG:1}P-Sts',\
 '14 IG_HRFM':'XF:05IDD-VA:1{Mir:4-CCG:1}P-Sts',\
 '00 HV_MASK':'XF:05IDA-VA:0{Msk:1-IP:1}Err:Supply-Sts',\
 '01 HV_BC1':'XF:05IDA-VA:0{BC:1-IP:1}Err:Supply-Sts',\
 '02 HV_BT-A':'XF:05IDA-VA:1{BT:1-IP:1}Err:Supply-Sts',\
 '03 HV_BC2':'XF:05IDA-VA:1{BC:2-IP:1}Err:Supply-Sts',\
 '04 HV_HFM':'XF:05IDA-VA:1{Mir:1-IP:1}Err:Supply-Sts',\
 '05 HV_DCM':'XF:05IDA-VA:1{Mono:HDCM-IP:1}Err:Supply-Sts',\
 '06 HV_BPM1':'XF:05IDA-VA:1{BPM:1-IP:1}Err:Supply-Sts',\
 '07 HV_SH-A':'XF:05IDA-VA:1{PSh:2-IP:1}Err:Supply-Sts',\
 '08 HV_BT-B':'XF:05IDB-VA:1{BT:1-IP:1}Err:Supply-Sts',\
 '09 HV_BPM2':'XF:05IDB-VA:1{BPM:2-IP:1}Err:Supply-Sts',\
 '10 HV_SH-B':'XF:05IDB-VA:1{PSh:4-IP:1}Err:Supply-Sts',\
 '11 HV_BT-C':'XF:05IDD-VA:1{BT:1-IP:1}Err:Supply-Sts',\
 '12 HV_BT-D':'XF:05IDD-VA:1{BT:1-IP:2}Err:Supply-Sts',\
 '13 HV_HFFM':'XF:05IDD-VA:1{Mir:2-IP:1}Err:Supply-Sts',\
 '14 HV_HRFM':'XF:05IDD-VA:1{Mir:4-IP:1}Err:Supply-Sts'\
}
ierrlist=dict((errlist[j],j) for j in errlist.keys())

tlist={#
 '00 T_MASK':['XF:05IDA-OP:1{Msk:1}T:TU-I',32.9,33.5],\
 '01 T_BC1':['XF:05IDA-OP:1{Fltr:1}T:H2OOut-I',29.8,30.5],\
 '02 T_BT-A':['XF:05IDA-OP:1{Slt:1U}T:TU-I',30.1,30.5],\
 '03 T_BC2':['XF:05IDA-OP:1{Mir:1}T:MskWtrOut-I',29.8,30.5],\
 '04 T_HFM':['XF:05IDA-OP:1{BS:WB}T:B-I',29.8,30.5],\
 '05 T_DCM':['XF:05IDA-OP:1{BS:PB}T:B-I',29.8,30.5],\
 '06 T_BPM1':['XF:05IDA-OP:1{Mono:HDCM}T:LN2Out-I',-173.,-165.],\
 '07 T_SH-A':['XF:05IDA-OP:1{Mono:HDCM-Ax:P}T-I',120.,140.] 
}
itlist=dict((tlist[j][0],j) for j in tlist.keys())

shutlist={#0 open, 1 closed
 '00':'XF:05ID-PPS{Sh:WB}Sts:Cls-Sts',\
 '07':'XF:05IDA-PPS:1{PSh:2}Sts:Cls-Sts',\
 '12':'XF:05IDB-PPS:1{PSh:4}Sts:Cls-Sts'\
}
ishutlist=dict((shutlist[j],j) for j in shutlist.keys())
#initialize alarm arrays.  0 is no fault, 1 is minor fault, 2 is severe fault
gvalarm=dict.fromkeys(gvlist.keys(),numpy.zeros((len(gvlist),),dtype=int))
#init shutter alarm
shalarm=dict.fromkeys(shutlist.keys(),numpy.zeros((len(shutlist),),dtype=int))
#erralarm=dict.fromkeys(errlist.keys(),numpy.zeros((len(errlist),),dtype=int))
erralarm={k: [] for k in errlist.keys()}
ccgalarm=dict.fromkeys(ccglist.keys(),numpy.zeros((len(ccglist),),dtype=float))
talarm=dict.fromkeys(tlist.keys(),numpy.zeros((len(tlist),),dtype=float))
flowalarm=dict.fromkeys(flowlist.keys(),numpy.zeros((len(flowlist),),dtype=float))

#signal handler
#catch ctrl-c
def sigint_handler(signal,frame):
        sys.stdout.write('\n')
        sys.stdout.flush()
        sys.exit()
signal.signal(signal.SIGINT,sigint_handler)

#call back functions to look up dict key and compare to limits (not needed for valves), report alarm
def cbftemp(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global talarm
    global itlist
    global tlist
    global tobj
    global pending_update
    #introduce bound value that is equal to either the PV or the object's return
    if pvname == 'XF:05IDA-OP:1{Msk:1}T:TU-I':
        oldvalue=talarm[itlist[pvname]]
        bvalue=tobj.avgm1u()
    elif pvname == 'XF:05IDA-OP:1{Slt:1U}T:TU-I':
        oldvalue=talarm[itlist[pvname]]
        bvalue=tobj.avgwbslu()
    else: 
        oldvalue=talarm[itlist[pvname]]
        bvalue=value
    if bvalue>tlist[itlist[pvname]][1] and bvalue<=tlist[itlist[pvname]][2]:
        talarm[itlist[pvname]]=ww_str
    elif bvalue>tlist[itlist[pvname]][2] or value ==0.0:
        talarm[itlist[pvname]]=ee_str
    else:
        talarm[itlist[pvname]]=ok_str
    if oldvalue is not talarm[itlist[pvname]]:
        pending_update=True
def cbfgv(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global gvalarm
    global igvlist
    global pending_update
    oldvalue=gvalarm[igvlist[pvname]]
    if value == 0:
        gvalarm[igvlist[pvname]]=ee_str
    else:
        gvalarm[igvlist[pvname]]=ok_str
    if oldvalue is not gvalarm[igvlist[pvname]]:
        pending_update=True
def cbfsh(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global shalarm
    global ishutlist
    global pending_update
    oldvalue=shalarm[ishutlist[pvname]]
    if value == 0:
        shalarm[ishutlist[pvname]]=ok_str
    else:
        shalarm[ishutlist[pvname]]=ee_str
    if oldvalue is not shalarm[ishutlist[pvname]]:
        pending_update=True
def cbferr(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global erralarm
    global ierrlist
    global pending_update
    oldvalue=erralarm[ierrlist[pvname]]
    if value is not 0:
        erralarm[ierrlist[pvname]]=ee_str
    else:
        erralarm[ierrlist[pvname]]=ok_str
    if oldvalue is not erralarm[ierrlist[pvname]]:
        pending_update=True
def cbfccg(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global ccgalarm
    global iccglist
    global ccglist
    global pending_update
    oldvalue=ccgalarm[iccglist[pvname]]
    if value>ccglist[iccglist[pvname]][1] and value<=ccglist[iccglist[pvname]][2]:
        ccgalarm[iccglist[pvname]]=ww_str
    elif value>ccglist[iccglist[pvname]][2] or value ==0.0:
        ccgalarm[iccglist[pvname]]=ee_str
    else:
        ccgalarm[iccglist[pvname]]=ok_str
    if oldvalue is not ccgalarm[iccglist[pvname]]:
        pending_update=True
def cbfflow(pvname=None,value=None,char_value=None,type=None,enum_strs=None,**kw):
    global flowalarm
    global flowlist
    global iflowlist
    global pending_update
    oldvalue=flowalarm[iflowlist[pvname]]
    if value<flowlist[iflowlist[pvname]][1] and value>=flowlist[iflowlist[pvname]][2]:
        flowalarm[iflowlist[pvname]]=ww_str
    elif value<flowlist[iflowlist[pvname]][2] or value ==0.0:
        flowalarm[iflowlist[pvname]]=ee_str
    else:
        flowalarm[iflowlist[pvname]]=ok_str
    if oldvalue is not flowalarm[iflowlist[pvname]]:
        pending_update=True
#primary function to handle commandline parameterization
def main(argv=None):
    global gvalarm
    global ccgalarm
    global gvlist
    global ccglist
    global igvlist
    global iccglist
    global errlist
    global ierrlist
    global erralarm
    global flowalarm
    global flowlist
    global iflowlist
    global pending_update
    #console update flag
    pending_update=True
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("--snapshot", action="store_true", dest="snap", default="False",help="print one status message and exit")
    (options,args) = parser.parse_args()
    #add pvs, initialize alarm states
    ID05err=epics.Device()
    for name in errlist.keys():
        ID05err.add_pv(errlist[name])   
        #delay for epics and pyepics to shake hands
        time.sleep(0.03)
        ID05err.PV(errlist[name]).get()
        if ID05err.get(errlist[name]) is not 0:
            erralarm[name]=ee_str
        else:
            erralarm[name]=ok_str
        ID05err.add_callback(errlist[name],cbferr)
    #pyepics device consisting of all CCGs
    ID05ccg=epics.Device()
    for name in ccglist.keys():
        ID05ccg.add_pv(ccglist[name][0])
        time.sleep(0.03)
        ID05ccg.PV(ccglist[name][0]).get()
        #initialize alarm list
        tval=float(ID05ccg.get(ccglist[name][0]))
        if tval>float(ccglist[name][1]) and tval<=float(ccglist[name][2]):
            ccgalarm[name]=ww_str
        elif tval>float(ccglist[name][2]):
            ccgalarm[name]=ee_str
        else:
            ccgalarm[name]=ok_str
        #install callbacks
        ID05ccg.add_callback(ccglist[name][0],cbfccg)
    ID05flow=epics.Device()
    for name in tlist.keys():
        #initialize alarm list
        tval=float(tobj.temp.get(tlist[name][0]))
        if tval>float(tlist[name][1]) and tval<=float(tlist[name][2]):
            talarm[name]=ww_str
        elif tval>float(tlist[name][2]):
            talarm[name]=ee_str
        else:
            talarm[name]=ok_str
        #install callbacks
        tobj.temp.add_callback(tlist[name][0],cbftemp)
    for name in flowlist.keys():
        ID05flow.add_pv(flowlist[name][0])
        time.sleep(0.03)
        ID05flow.PV(flowlist[name][0]).get()
        #initialize alarm list
        tval=float(ID05flow.get(flowlist[name][0]))
        if tval<float(flowlist[name][1]) and tval>=float(flowlist[name][2]):
            flowalarm[name]=ww_str
        elif tval<float(flowlist[name][2]):
            flowalarm[name]=ee_str
        else:
            flowalarm[name]=ok_str
        #install callbacks
        ID05flow.add_callback(flowlist[name][0],cbfflow)
    #pyepics device consisting of all gate valves
    ID05gv=epics.Device()
    for name in gvlist.keys():
        ID05gv.add_pv(gvlist[name]) 
        time.sleep(0.03)
        ID05gv.PV(gvlist[name]).get()
        if ID05gv.get(gvlist[name]) == 0:
            gvalarm[name]=ee_str
        else:
            gvalarm[name]=ok_str
        ID05gv.add_callback(gvlist[name],cbfgv)
    #pyepics device consisting of all shutters
    ID05sh=epics.Device()
    for name in shutlist.keys():
        ID05sh.add_pv(shutlist[name])
        time.sleep(0.03)
        ID05sh.PV(shutlist[name]).get()
        if ID05sh.get(shutlist[name]) == 0:
            shalarm[name]=ok_str
        else:
            shalarm[name]=ee_str
        ID05sh.add_callback(shutlist[name],cbfsh)
    #force an update at least once every 30 sec
    t_old=time.time()
    while True:
        if pending_update==True:
            fflag_fe=fflag_a=fflag_b=fflag_d=False
            wflag_fe=wflag_a=wflag_b=wflag_d=False
            os.system('clear')
            pending_update=False
            Ngv=1
            #list of lists for terminaltables
            trow=list()
            #first row of table is labeling
            trow.append(['CC GAUGE','STAT','PUMP HV','STAT','GATEVALVE','STAT','FLOW','STAT','RTD','STAT'])
            #CCG list is most comprehensive
            for name in sorted(hvlist.keys()):
                s=name.rsplit(' ')[0]+' IG_'+name.rsplit('_')[1]
                if ccgalarm.has_key(s):
                    if erralarm[s] == ee_str:
                        alarm=ee_str
                    else:
                        alarm=ccgalarm[s]
                    trow.append([ccglist[s][0].rsplit('{')[1].rsplit('}')[0]])
                    #trow[Ngv].append(ccgalarm[s])
                    if alarm==ok_str:
                        istr=oktext("%1.0e"%ID05ccg.get(ccglist[s][0]))
                    elif alarm==ww_str:
                        istr=wwtext("%1.0e"%ID05ccg.get(ccglist[s][0]))
                    else:
                        istr=eetext("%1.0e"%ID05ccg.get(ccglist[s][0]))
                        if name.rsplit(' ')[0] < 8:
                            fflag_a=True
                        elif name.rsplit(' ')[0] < 11:
                            fflag_b=True
                        else:
                            fflag_d=True
                    trow[Ngv].append(istr)
                else:
                    trow.append([''])
                    trow[Ngv].append('')
                #create keys for HV list 
                s=name.rsplit(' ')[0]+' HV_'+name.rsplit('_')[1]
                #check for status errors
                if erralarm.has_key(s):
                    trow[Ngv].append(errlist[s].rsplit('{')[1].rsplit('}')[0])
                    trow[Ngv].append(erralarm[s])
                else:
                    trow[Ngv].append('')
                    trow[Ngv].append('')
                #create potential keys for the gate valves
                s=name.rsplit(' ')[0]+' GV_'+name.rsplit('_')[1]
                #check for closed gate valves
                if gvalarm.has_key(s):
                    trow[Ngv].append(gvlist[s].rsplit('{')[1].rsplit('}')[0])
                    trow[Ngv].append(gvalarm[s])
                    if gvalarm[s]==ee_str:
                        if int(name.rsplit(' ')[0])==0:
                            fflag_fe=True
                        elif int(name.rsplit(' ')[0])<8:
                            wflag_a=True
                        elif int(name.rsplit(' ')[0])<11:
                            wflag_b=True
                        else:
                            wflag_d=True
                else:
                    trow[Ngv].append('')
                    trow[Ngv].append('')
                s=name.rsplit(' ')[0]+' FL_'+name.rsplit('_')[1]
                if flowalarm.has_key(s):
                    trow[Ngv].append(flowlist[s][0].rsplit('{')[1].rsplit('}')[0])
                    alarm=flowalarm[s]
                    if alarm==ok_str:
                        istr=oktext("%4.2f"%ID05flow.get(flowlist[s][0]))
                    elif alarm==ww_str:
                        istr=wwtext("%4.2f"%ID05flow.get(flowlist[s][0]))
                    else:
                        istr=eetext("%4.2f"%ID05flow.get(flowlist[s][0]))
                        fflag_a=True    
                    trow[Ngv].append(istr)
                else:
                    trow[Ngv].append('')
                    trow[Ngv].append('')
                s=name.rsplit(' ')[0]+' T_'+name.rsplit('_')[1]
                if talarm.has_key(s):
                    trow[Ngv].append(tlist[s][0].rsplit('{')[1].rsplit('}')[0])
                    alarm=talarm[s]
                    if tlist[s][0] == 'XF:05IDA-OP:1{Msk:1}T:TU-I':
                        ivalue=tobj.avgm1u()
                    elif tlist[s][0] == 'XF:05IDA-OP:1{Slt:1U}T:TU-I':
                        ivalue=tobj.avgwbslu()
                    else:
                        ivalue=tobj.temp.get(tlist[s][0])
                    if alarm==ok_str:
                        istr=oktext("%6.1f"%ivalue)
                    elif alarm==ww_str:
                        istr=wwtext("%6.1f"%ivalue)
                    else:
                        istr=eetext("%6.1f"%ivalue)
                        fflag_a=True
                    trow[Ngv].append(istr)
                else:
                    trow[Ngv].append('')
                    trow[Ngv].append('')
                Ngv=Ngv+1
            table=terminaltables.UnixTable(trow)
#            sys.stdout.write(table.table)
            if shalarm['00']==ee_str and fflag_fe==False and wflag_fe==False:
                fflag_fe=True
            if shalarm['07']==ee_str and fflag_b==False and wflag_b==False:
                fflag_b=True
            if shalarm['12']==ee_str and fflag_d==False and wflag_d==False:
                fflag_d=True
            nrow=list()
            if fflag_fe==True:
                nrow.append(eetext('FRONT END'))
            else:
                nrow.append(oktext('FRONT END'))
            if fflag_a==True:
                nrow.append(eetext('HUTCH A'))
            elif wflag_a==True:
                nrow.append(wwtext('HUTCH A'))
            else:
                nrow.append(oktext('HUTCH A'))
            if fflag_b==True:
                nrow.append(eetext('HUTCH B'))
            elif wflag_b==True:
                nrow.append(wwtext('HUTCH B'))
            else:
                nrow.append(oktext('HUTCH B'))
            if fflag_d==True:
                nrow.append(eetext('HUTCH D'))
            elif wflag_d==True:
                nrow.append(wwtext('HUTCH D'))
            else:
                nrow.append(oktext('HUTCH D'))
            istr='\n\t\t'
            for i in range(0,len(nrow)):
                istr=istr+nrow[i]+'\t\t\t'
            istr=istr+'\t'
#            sys.stdout.write(istr)
#            sys.stdout.flush()
            msg = table.table+istr
            if options.snap==True:
                print(msg)
                break
            sys.stdout.write(msg)
            sys.stdout.flush()
        epics.poll(evt=1.e-3,iot=0.1)
        if (time.time()-t_old) > 30.:
            t_old=time.time()
            pending_update=True

if __name__ == "__main__":
    sys.exit(main())
    
