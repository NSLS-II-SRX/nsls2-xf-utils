#!/usr/bin/env /usr/bin/python2.7
import os
import epics
import numpy
import sys
import time
import signal
import string
from colorclass import Color as col
import terminaltables
import srxfe,srxbpm 

def sigint_handler(signal,frame):
	sys.stdout.write('\n')
	sys.stdout.flush()
	sys.exit()
signal.signal(signal.SIGINT,sigint_handler)
numpy.seterr(divide='ignore',invalid='ignore')

ok_str=col('{autoblue}OK{/autoblue}')
ee_str=col('{autored}EE{/autored}')
ww_str=col('{autoyellow}WW{/autoyellow}')
def oktext(s):
	return col('{autoblue}%s{/autoblue}'%s)
def wwtext(s):
	return col('{autoyellow}%s{/autoyellow}'%s)
def eetext(s):
	return col('{autored}%s{/autored}'%s)
thresh={#index:[expected value, half-margin of error]
 'bpm1x':[0.000,0.01],\
 'bpm1y':[0.000,0.01],\
 'bpm2x':[0.000,0.01],\
 'bpm2y':[0.000,0.01],\
# 'trajax':[-0.010,0.005],\
# 'trajay':[0.005,0.005],\
# 'trajax':[-0.020,0.005],\
# 'trajay':[0.005,0.005],\
 'trajax':[-0.020,0.005],\
 'trajay':[0.000,0.005],\
 'trajox':[0.000,0.020],\
 'trajoy':[0.000,0.020],\
 'bba8x':[-7.8000e-02,0.],\
 'bba8y':[-3.2000e-02,0.],\
 'bba9x':[-8.0400e-01,0.],\
 'bba9y':[-7.4300e-01,0.]\
}
target={#key:[targets in order of - to + motor position]
 'bpm1':['diode','open','Cu foil','Ti foil','YAG'],\
 'bpm2':['diode','open','Cu foil','Ti foil','YAG']\
}
def check_value(key,value):
	if value == None:
		return eetext("NaN")
	if value == 0:
		value=1000.
	nval=numpy.abs(thresh[key][0] - value)
	if nval <= thresh[key][1]:
		return oktext("%(V)7.4e"%{'V':value})
	elif nval < 2.*thresh[key][1]:
		return wwtext("%(V)7.4e"%{'V':value})
	else:
		return eetext("%(V)7.4e"%{'V':value})
def check_foil(key,value):
	if value ==None:
		return eetext("NaN")
	if numpy.abs(-50. - value) <= 1.:
		return wwtext(target[key][0])
	elif numpy.abs(-25. - value) <= 1.:
		return eetext(target[key][1])
	elif numpy.abs(0.0 - value) <= 1.:
		return oktext(target[key][2])
	elif numpy.abs(25. - value) <= 1.:
		return oktext(target[key][3])
	elif numpy.abs(50. - value) <= 1.:
		return wwtext(target[key][4])
	else:
		return eetext("OOP")
#primary function to handle commandline parameterization
def main(argv=None):
	bpm1=srxbpm.nsls2bpm(bpm='bpm1')
	bpm2=srxbpm.nsls2bpm(bpm='bpm2')
	fe=srxfe.nsls2fe()
	SRcurrent=epics.PV('SR:C03-BI{DCCT:1}I:Real-I')
	SRcurrent.info
	Mshutters=epics.PV('SR-EPS{PLC:1}Sts:MstrSh-Sts')
	Mshutters.info
	time.sleep(0.1)
	while True:
		#list of lists for terminaltables
		trow=list()
		#first row of table is labeling
		os.system('clear')
		bbalist=fe.BBA()
		trow.append(['HUTCHES','X/Y','FRONT-END','X','Y'])
		trow.append(['BPM1',check_value('bpm1x',bpm1.H()),'TRAJ ANG',check_value('trajax',fe.AX()),check_value('trajay',fe.AY())])
		trow.append([check_foil('bpm1',bpm1.foil()),check_value('bpm1y',bpm1.V()),'TRAJ OFF',check_value('trajox',fe.OX()),check_value('trajoy',fe.OY())])
		trow.append(['BPM2',check_value('bpm2x',bpm2.H()),'BBA BPM8',check_value('bba8x',bbalist['bba8x']),check_value('bba8y',bbalist['bba8y'])])
		trow.append([check_foil('bpm2',bpm2.foil()),check_value('bpm2y',bpm2.V()),'BBA BPM9',check_value('bba9x',bbalist['bba9x']),check_value('bba9y',bbalist['bba9y'])])
		table=terminaltables.UnixTable(trow)
		sys.stdout.write(table.table)
		msg='\n'
		current=SRcurrent.get()
		if current>20.:
			msg=msg+oktext('\t%5.1fmA Stored\t\t\t'%current)
		else:
			msg=msg+eetext('\t%5.1fmA Stored\t\t\t'%current)
		MSstatus=Mshutters.get()
		if MSstatus == 1:
			msg=msg+oktext('Shutters Enabled')
		else:
			msg=msg+eetext('Shutters Disabled')
		sys.stdout.write(msg)
		sys.stdout.flush()
		time.sleep(5.)

if __name__ == "__main__":
	sys.exit(main())
	
