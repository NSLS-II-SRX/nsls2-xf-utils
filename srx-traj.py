#! /usr/bin/env python
import sys
import time
import math
import epics
import os
import string
from optparse import OptionParser

ox=epics.PV('SR:C31-{AI}Aie5:Offset-x-Cal')
oy=epics.PV('SR:C31-{AI}Aie5:Offset-y-Cal')
ax=epics.PV('SR:C31-{AI}Aie5:Angle-x-Cal')
ay=epics.PV('SR:C31-{AI}Aie5:Angle-y-Cal')
ox2=epics.PV('SR:C31-{AI}Aie5-2:Offset-x-Cal')
oy2=epics.PV('SR:C31-{AI}Aie5-2:Offset-y-Cal')
ax2=epics.PV('SR:C31-{AI}Aie5-2:Angle-x-Cal')
ay2=epics.PV('SR:C31-{AI}Aie5-2:Angle-y-Cal')
fpga_ox1=epics.PV('SR:C31-{AI}5:FPGA:x_mm-I')
#SRX == '-2' pvs
fpga_ox2=epics.PV('SR:C31-{AI}5-2:FPGA:x_mm-I')
fpga_ax1=epics.PV('SR:C31-{AI}5:FPGA:x_mrad-I')
fpga_ax2=epics.PV('SR:C31-{AI}5-2:FPGA:x_mrad-I')
fpga_oy1=epics.PV('SR:C31-{AI}5:FPGA:y_mm-I')
fpga_oy2=epics.PV('SR:C31-{AI}5-2:FPGA:y_mm-I')
fpga_ay1=epics.PV('SR:C31-{AI}5:FPGA:y_mrad-I')
fpga_ay2=epics.PV('SR:C31-{AI}5-2:FPGA:y_mrad-I')
bba_bmp8x=epics.PV('SR:C05-BI{BPM:8}BbaXOff-SP')
bba_bmp8y=epics.PV('SR:C05-BI{BPM:8}BbaYOff-SP')
bba_bmp9x=epics.PV('SR:C05-BI{BPM:9}BbaXOff-SP')
bba_bmp9y=epics.PV('SR:C05-BI{BPM:9}BbaYOff-SP')

s3in=epics.PV('FE:C05A-OP{Slt:3-Ax:I}Mtr.RBV')
s3top=epics.PV('FE:C05A-OP{Slt:3-Ax:T}Mtr.RBV')
s4out=epics.PV('FE:C05A-OP{Slt:4-Ax:O}Mtr.RBV')
s4bot=epics.PV('FE:C05A-OP{Slt:4-Ax:B}Mtr.RBV')

ox.info
oy.info
ax.info
ay.info
ox2.info
oy2.info
ax2.info
ay2.info
fpga_ox1.info
fpga_ox2.info
fpga_ax1.info
fpga_ax2.info
fpga_oy1.info
fpga_oy2.info
fpga_ay1.info
fpga_ay2.info
bba_bmp8x.info
bba_bmp8y.info
bba_bmp9x.info
bba_bmp9y.info

def main(argv=None):

       #parse command line options
        usage = "usage: %prog [options]\n"
        parser = OptionParser(usage)
        parser.add_option("--nowrite", action="store_true", dest="nowrite", default=False, help="do not write information to file")

        (options,args) = parser.parse_args()

	if options.nowrite is not True:
	        #open log file
	        D0=time.localtime()[0]
	        D1=time.localtime()[1]
	        D2=time.localtime()[2]
	        D3=time.localtime()[3]
	        D4=time.localtime()[4]
	        cd=os.getcwd()
	        fstr='/nfs/xf05id1/data/'
	        if sys.argv[0][0]=='.':
	                out_filename=fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'log_'+repr(D3)+'_'+repr(D4)+'_'+\
	                 string.split(string.strip(sys.argv[0],'./'),'/')[0]+'.txt'
	        else:
	                out_filename=fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)+'/'+'log_'+repr(D3)+'_'+repr(D4)+'_'+\
	                 string.split(string.strip(sys.argv[0],'./'),'/')[5]+'.txt'
	        try:
	                os.chdir(fstr+repr(D0))
	        except OSError:
	                try:    
	                        os.mkdir(fstr+repr(D0))
	                except Exception:
	                        print 'cannot create directory: '+fstr+repr(D0)
	                        sys.exit()
	
	        try:
	                os.chdir(fstr+repr(D0)+'/'+repr(D1))
	        except OSError:
	                try:
	                        os.mkdir(fstr+repr(D0)+'/'+repr(D1))
	                except Exception:
	                        print 'cannot create directory: '+fstr+repr(D0)+'/'+repr(D1)
	                        sys.exit()
	        try:
	                os.chdir(fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2))
	        except OSError:
	                try:
	                        os.mkdir(fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2))
	                except Exception:
	                        print 'cannot create directory: '+fstr+repr(D0)+'/'+repr(D1)+'/'+repr(D2)
	                        sys.exit()
	        try:
	                fp=open(out_filename,'a')
	        except Exception:
	                print 'cannot open file: '+out_filename
	                sys.exit()
	        os.chdir(cd)


	tstr="#***\nNew PVs: Offset X = %(OX)6.3f Offset Y = %(OY)6.3f Angle X = %(AX)6.3f Angle Y = %(AY)6.3f"%\
	{"OX":ox2.get(),"OY":oy2.get(),"AX":ax2.get(),"AY":ay2.get()}
	print tstr
	if options.nowrite is not True:
		fp.write(tstr+'\n')
	tstr="BBA: Offset 8X = %(OX)6.3f Offset 8Y = %(OY)6.3f Offset 9X = %(AX)6.3f Offset 9Y = %(AY)6.3f\n#***\n"%\
	{"OX":bba_bmp8x.get(),"OY":bba_bmp8y.get(),"AX":bba_bmp9x.get(),"AY":bba_bmp9y.get()}
	print tstr
	if options.nowrite is not True:
		fp.write(tstr+'\n')
	tstr="Offset X = %(OX)6.3f Offset Y = %(OY)6.3f Angle X = %(AX)6.3f Angle Y = %(AY)6.3f"%\
	{"OX":ox.get(),"OY":oy.get(),"AX":ax.get(),"AY":ay.get()}
	print tstr
	if options.nowrite is not True:
		fp.write(tstr+'\n')
	tstr="FE slits S3-Inb= %(SI)9.5f S3-Top= %(ST)9.5f S4-Out= %(SO)9.5f S4-Bot= %(SB)9.5f"%\
	{"SI":s3in.get(),"ST":s3top.get(),"SO":s4out.get(),"SB":s4bot.get()}
	print tstr
	if options.nowrite is not True:
		fp.write(tstr+'\n')
	tstr="FPGA calculated Offset X1 = %(OX)6.3f X2 = %(OX2)6.3f Offset Y1 = %(OY)6.3f Offset Y2 = %(OY2)6.3f\nAngle X1 = %(AX)6.3f Angle X2 = %(AX2)6.3f Angle Y1 = %(AY)6.3f Angle Y2 = %(AY2)6.3f"%\
	{"OX":fpga_ox1.get(),"OX2":fpga_ox2.get(),"OY":fpga_oy1.get(),"OY2":fpga_oy2.get(), "AX":fpga_ax1.get(),"AX2":fpga_ax2.get(),"AY":fpga_ay1.get(),"AY2":fpga_ay2.get()}
	print tstr
	if options.nowrite is not True:
		fp.write(tstr+'\n')
		fp.close()

if __name__ == "__main__":
        sys.exit(main())

