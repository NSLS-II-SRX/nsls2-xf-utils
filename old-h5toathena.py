#! /usr/bin/python2.7 
# convert from the h5 produced at SRX to something that Athena will understand
import h5py
import math
import sys
import os
import time
from optparse import OptionParser

global d
#Si 111
d=3.1355
global sddfactor
sddfactor=[9.9936]

def dcmtoeV(angle=0.):
    return 12398. / (2. * d * math.sin(angle/180.*3.1416))
def chtoeV(ch=0):
    global sddfactor
    return (ch+1)*sddfactor[0]

def main(argv=None):

    usage="usage: %prog [options]"
    parser=OptionParser(usage)
    parser.add_option("--input",action="store",type="string",dest="h5name",\
     help="name of HDF5 to convert")
    parser.add_option("--output",action="store",type="string",dest="ofile",\
     help="base name of output file")
    (options,args) = parser.parse_args()

    try:
        h5=h5py.File(options.h5name)
    except OSError:
        print '%s: file could not be opened!'%options.h5name
        sys.exit()

    datapath='/entry/instrument/detector/data'

    sh=rawdata.shape
    if len(sh) == 3:
        #no virtual dimensions
        try:
            fp=open(options.ofile,mode='x')
        except OSError:
            print '%s: file could not be opened!'%options.ofile
            sys.exit()
        except FileExistsError:
            print '%s: file exists!'%options.ofile
            sys.exit()
        rawdata=h5[datapath]
        data=numpy.asarray(rawdata)
        procdata=numpy.zeros(data[0][0][:].shape)
        #sum over all exposures
        for i in range(0,sh[0]):
            #sum data in the first three channels
            for j in range(0,3):
                procdata=procdata+data[i][j]
            s="# NSLS-II SRX\n# created from %(H5)s on %(T)s\n# ----------\n# energy counts\n"\
             %{"H5":options.h5name, "T":time.asctime()}
            fp.write(s)
            for i in range(0,len(procdata)):
                s="%(energy)8.2f\t%(ct)d\n"%{"energy":chtoeV(i),"ct":procdata[i]}
                fp.write(s)
        fp.close()
    elif len(sh)==4:
        #one virtual dimension
        for k in range(0,sh[0]):
            fname=options.ofile+"_%05d"%k
            try:
                fp=open(fname,mode='x')
            except OSError:
                print '%s: file could not be opened!'%options.ofile
                sys.exit()
            except FileExistsError:
                print '%s: file exists!'%options.ofile
                sys.exit()
            rawdata=h5[datapath][k]
            data=numpy.asarray(rawdata)
            procdata=numpy.zeros(data[0][0][:].shape)
            #sum over all exposures
            for i in range(0,sh[0]):
                #sum data in the first three channels
                for j in range(0,3):
                    procdata=procdata+data[i][j]
            s="# NSLS-II SRX\n# created from %(H5)s on %(T)s\n# ----------\n# energy counts\n"\
             %{"H5":options.h5name, "T":time.asctime()}
            fp.write(s)
            for i in range(0,len(procdata)):
                s="%(energy)8.2f\t%(ct)d\n"%{"energy":chtoeV(i),"ct":procdata[i]}
                fp.write(s)
            fp.close()
    elif len(sh)==5:
        #two virtual dimensions
        pass
    else:
        print "Data has unknown shape: %s"%sh
        sys.exit()
