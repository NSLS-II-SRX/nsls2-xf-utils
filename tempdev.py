import epics
import time

epstemplist={#
 '00 T_MASK1-TU':'XF:05IDA-OP:1{Msk:1}T:TU-I',\
 '00 T_MASK1-BU':'XF:05IDA-OP:1{Msk:1}T:BU-I',\
 '00 T_MASK1-IU':'XF:05IDA-OP:1{Msk:1}T:IU-I',\
 '00 T_MASK1-OU':'XF:05IDA-OP:1{Msk:1}T:OU-I',\
 '00 T_MASK1-TD':'XF:05IDA-OP:1{Msk:1}T:TD-I',\
 '00 T_MASK1-BD':'XF:05IDA-OP:1{Msk:1}T:BD-I',\
 '00 T_MASK1-ID':'XF:05IDA-OP:1{Msk:1}T:ID-I',\
 '00 T_MASK1-OD':'XF:05IDA-OP:1{Msk:1}T:OD-I',\
 '00 T_MASK2-TU':'XF:05IDA-OP:1{Msk:2}T:TU-I',\
 '00 T_MASK2-BU':'XF:05IDA-OP:1{Msk:2}T:BU-I',\
 '00 T_MASK2-IU':'XF:05IDA-OP:1{Msk:2}T:IU-I',\
 '00 T_MASK2-OU':'XF:05IDA-OP:1{Msk:2}T:OU-I',\
 '00 T_MASK2-TD':'XF:05IDA-OP:1{Msk:2}T:TD-I',\
 '00 T_MASK2-BD':'XF:05IDA-OP:1{Msk:2}T:BD-I',\
 '00 T_MASK2-ID':'XF:05IDA-OP:1{Msk:2}T:ID-I',\
 '00 T_MASK2-OD':'XF:05IDA-OP:1{Msk:2}T:OD-I',\
 '02 T_DIA0':'XF:05IDA-OP:1{Fltr:1}T:H2OIn-I',\
 '02 T_DIA1':'XF:05IDA-OP:1{Fltr:1}T:H2OOut-I',\
 '03 T_WBS1-TU':'XF:05IDA-OP:1{Slt:1U}T:TU-I',\
 '03 T_WBS1-BU':'XF:05IDA-OP:1{Slt:1U}T:BU-I',\
 '03 T_WBS1-IU':'XF:05IDA-OP:1{Slt:1U}T:IU-I',\
 '03 T_WBS1-OU':'XF:05IDA-OP:1{Slt:1U}T:OU-I',\
 '03 T_WBS1-TD':'XF:05IDA-OP:1{Slt:1U}T:TD-I',\
 '03 T_WBS1-BD':'XF:05IDA-OP:1{Slt:1U}T:BD-I',\
 '03 T_WBS1-ID':'XF:05IDA-OP:1{Slt:1U}T:ID-I',\
 '03 T_WBS1-OD':'XF:05IDA-OP:1{Slt:1U}T:OD-I',\
 '03 T_WBS2-TU':'XF:05IDA-OP:1{Slt:1D}T:TU-I',\
 '03 T_WBS2-BU':'XF:05IDA-OP:1{Slt:1D}T:BU-I',\
 '03 T_WBS2-IU':'XF:05IDA-OP:1{Slt:1D}T:IU-I',\
 '03 T_WBS2-OU':'XF:05IDA-OP:1{Slt:1D}T:OU-I',\
 '03 T_WBS2-TD':'XF:05IDA-OP:1{Slt:1D}T:TD-I',\
 '03 T_WBS2-BD':'XF:05IDA-OP:1{Slt:1D}T:BD-I',\
 '03 T_WBS2-ID':'XF:05IDA-OP:1{Slt:1D}T:ID-I',\
 '03 T_WBS2-OD':'XF:05IDA-OP:1{Slt:1D}T:OD-I',\
 '04 T_HFM-IDM':'XF:05IDA-OP:1{Mir:1}T:MskI-I',\
 '04 T_HFM-ODM':'XF:05IDA-OP:1{Mir:1}T:MskO-I',\
 '04 T_HFM-MW0':'XF:05IDA-OP:1{Mir:1}T:MskWtrIn-I',\
 '04 T_HFM-MW1':'XF:05IDA-OP:1{Mir:1}T:MskWtrOut-I',\
 '04 T_HFM-MIR':'XF:05IDA-OP:1{Mir:1}T-I',\
 '04 T_HFM-P':'XF:05IDA-OP:1{Mir:1-Ax:P}T-I',\
 '04 T_HFM-X':'XF:05IDA-OP:1{Mir:1-Ax:X}T-I',\
 '04 T_PBS1-TU':'XF:05IDA-OP:1{Slt:2U}T:TU-I',\
 '04 T_PBS1-BU':'XF:05IDA-OP:1{Slt:2U}T:BU-I',\
 '04 T_PBS1-IU':'XF:05IDA-OP:1{Slt:2U}T:IU-I',\
 '04 T_PBS1-OU':'XF:05IDA-OP:1{Slt:2U}T:OU-I',\
 '04 T_PBS1-TD':'XF:05IDA-OP:1{Slt:2U}T:TD-I',\
 '04 T_PBS1-BD':'XF:05IDA-OP:1{Slt:2U}T:BD-I',\
 '04 T_PBS1-ID':'XF:05IDA-OP:1{Slt:2U}T:ID-I',\
 '04 T_PBS1-OD':'XF:05IDA-OP:1{Slt:2U}T:OD-I',\
 '04 T_PBS2-TU':'XF:05IDA-OP:1{Slt:2D}T:TU-I',\
 '04 T_PBS2-BU':'XF:05IDA-OP:1{Slt:2D}T:BU-I',\
 '04 T_PBS2-IU':'XF:05IDA-OP:1{Slt:2D}T:IU-I',\
 '04 T_PBS2-OU':'XF:05IDA-OP:1{Slt:2D}T:OU-I',\
 '04 T_PBS2-TD':'XF:05IDA-OP:1{Slt:2D}T:TD-I',\
 '04 T_PBS2-BD':'XF:05IDA-OP:1{Slt:2D}T:BD-I',\
 '04 T_PBS2-ID':'XF:05IDA-OP:1{Slt:2D}T:ID-I',\
 '04 T_PBS2-OD':'XF:05IDA-OP:1{Slt:2D}T:OD-I',\
 '04 T_WBST1':'XF:05IDA-OP:1{BS:WB}T:T-I',\
 '04 T_WBST2':'XF:05IDA-OP:1{BS:WB}T:B-I',\
 '04 T_PBST1':'XF:05IDA-OP:1{BS:PB}T:T-I',\
 '04 T_PBST2':'XF:05IDA-OP:1{BS:PB}T:B-I',\
 '05 T_DCM-1-1':'XF:05IDA-OP:1{Mono:HDCM-C:111_1}T-I',\
 '05 T_DCM-2-1':'XF:05IDA-OP:1{Mono:HDCM-C:311_1}T-I',\
 '05 T_DCM-1-2':'XF:05IDA-OP:1{Mono:HDCM-C:111_2}T-I',\
 '05 T_DCM-2-2':'XF:05IDA-OP:1{Mono:HDCM-C:311_2}T-I',\
 '05 T_DCM-LNO':'XF:05IDA-OP:1{Mono:HDCM}T:LN2Out-I',\
 '05 T_DCM-TB':'XF:05IDA-OP:1{Mono:HDCM}T:TC-I',\
 '05 T_DCM-X':'XF:05IDA-OP:1{Mono:HDCM-Ax:X}T-I',\
 '05 T_DCM-P2':'XF:05IDA-OP:1{Mono:HDCM-Ax:P2}T-I',\
 '05 T_DCM-P':'XF:05IDA-OP:1{Mono:HDCM-Ax:P}T-I',\
 '05 T_DCM-P2':'XF:05IDA-OP:1{Mono:HDCM-Ax:P2}T-I',\
 '05 T_DCM-R':'XF:05IDA-OP:1{Mono:HDCM-Ax:R}T-I'\
}


class EPSTemperature():
	def __init__(self):
		self.temp=epics.Device()
		for name in epstemplist.keys():
			self.temp.add_pv(epstemplist[name])
			time.sleep(0.05)
			self.temp.PV(epstemplist[name]).info
	def avgm1u(self):
		return ( float(self.temp.get(epstemplist['00 T_MASK1-TU']))\
		 + float(self.temp.get(epstemplist['00 T_MASK1-BU']))\
		 + float(self.temp.get(epstemplist['00 T_MASK1-IU']))\
		 + float(self.temp.get(epstemplist['00 T_MASK1-OU'])) ) / 4.
	def avgm1d(self):
		return ( float(self.temp.get(epstemplist['00 T_MASK1-TD']))\
		 + float(self.temp.get(epstemplist['00 T_MASK1-BD']))\
		 + float(self.temp.get(epstemplist['00 T_MASK1-ID']))\
		 + float(self.temp.get(epstemplist['00 T_MASK1-OD'])) ) / 4.
	def avgm2u(self):
		return ( float(self.temp.get(epstemplist['00 T_MASK2-TU']))\
		 + float(self.temp.get(epstemplist['00 T_MASK2-BU']))\
		 + float(self.temp.get(epstemplist['00 T_MASK2-IU']))\
		 + float(self.temp.get(epstemplist['00 T_MASK2-OU'])) ) / 4.
	def avgm2d(self):
		return ( float(self.temp.get(epstemplist['00 T_MASK2-TD']))\
		 + float(self.temp.get(epstemplist['00 T_MASK2-BD']))\
		 + float(self.temp.get(epstemplist['00 T_MASK2-ID']))\
		 + float(self.temp.get(epstemplist['00 T_MASK2-OD'])) ) / 4.
	def avgfilt(self):
		return ( float(self.temp.get(epstemplist['02 T_DIA0']))\
		 + float(self.temp.get(epstemplist['02 T_DIA1'])) ) / 2.
	def avgwbslu(self):
		return ( float(self.temp.get(epstemplist['03 T_WBS1-TU']))\
		 + float(self.temp.get(epstemplist['03 T_WBS1-BU']))\
		 + float(self.temp.get(epstemplist['03 T_WBS1-IU']))\
		 + float(self.temp.get(epstemplist['03 T_WBS1-OU']))\
		 + float(self.temp.get(epstemplist['03 T_WBS1-TD']))\
		 + float(self.temp.get(epstemplist['03 T_WBS1-BD']))\
		 + float(self.temp.get(epstemplist['03 T_WBS1-ID']))\
		 + float(self.temp.get(epstemplist['03 T_WBS1-OD'])) ) / 8.
	def avgwbsld(self):
		return ( float(self.temp.get(epstemplist['03 T_WBS2-TU']))\
		 + float(self.temp.get(epstemplist['03 T_WBS2-BU']))\
		 + float(self.temp.get(epstemplist['03 T_WBS2-IU']))\
		 + float(self.temp.get(epstemplist['03 T_WBS2-OU']))\
		 + float(self.temp.get(epstemplist['03 T_WBS2-TD']))\
		 + float(self.temp.get(epstemplist['03 T_WBS2-BD']))\
		 + float(self.temp.get(epstemplist['03 T_WBS2-ID']))\
		 + float(self.temp.get(epstemplist['03 T_WBS2-OD'])) ) / 8.
	def avgpbslu(self):
		return ( float(self.temp.get(epstemplist['04 T_PBS1-TU']))\
		 + float(self.temp.get(epstemplist['04 T_PBS1-BU']))\
		 + float(self.temp.get(epstemplist['04 T_PBS1-IU']))\
		 + float(self.temp.get(epstemplist['04 T_PBS1-OU']))\
		 + float(self.temp.get(epstemplist['04 T_PBS1-TD']))\
		 + float(self.temp.get(epstemplist['04 T_PBS1-BD']))\
		 + float(self.temp.get(epstemplist['04 T_PBS1-ID']))\
		 + float(self.temp.get(epstemplist['04 T_PBS1-OD'])) ) / 8.
	def avgpbsld(self):
		return ( float(self.temp.get(epstemplist['04 T_PBS2-TU']))\
		 + float(self.temp.get(epstemplist['04 T_PBS2-BU']))\
		 + float(self.temp.get(epstemplist['04 T_PBS2-IU']))\
		 + float(self.temp.get(epstemplist['04 T_PBS2-OU']))\
		 + float(self.temp.get(epstemplist['04 T_PBS2-TD']))\
		 + float(self.temp.get(epstemplist['04 T_PBS2-BD']))\
		 + float(self.temp.get(epstemplist['04 T_PBS2-ID']))\
		 + float(self.temp.get(epstemplist['04 T_PBS2-OD'])) ) / 8.
	def avgwbst(self):
		return ( float(self.temp.get(epstemplist['04 T_WBST1']))\
		 + float(self.temp.get(epstemplist['04 T_WBST2'])) ) / 2.
	def avgpbst(self):
		return ( float(self.temp.get(epstemplist['04 T_PBST1']))\
		 + float(self.temp.get(epstemplist['04 T_PBST2'])) ) / 2.
