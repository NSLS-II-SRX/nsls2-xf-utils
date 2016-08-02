# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 17:22:39 2015

@author: xf05id1
"""

import pyxrf.model.fileio as fio
import string
import sys
import srxdatadir

#dfx3filedir = '/data/XSPRESS3/2015-3/in-house/'
#dfpyxrffoutdir='/nfs/xf05id1/data/pyxrf_analysis/unsorted/'

def x3toPyxrf(x3dir=srxdatadir.dfx3filedir, fileprefix=None, foutdir=srxdatadir.dfpyxrffoutdir, filenum=0):

    print 'input file directory:', x3dir

    if fileprefix == None:
        print "please provide a fileprefix as indicated in Xspress3 screen. E.g. '2015_10_25_21_14'"
        sys.exit()

    
    if fileprefix[-1] == '_':
        fileprefix=fileprefix[0:-1]
    fin=x3dir+fileprefix+'_'+str(filenum)+'.hdf5'
    print 'input file:', fileprefix+'_'+str(filenum)
    print 'ouput file directory:', foutdir

    dirf = string.split(fileprefix, sep='_')
    textfiledir = '/nfs/xf05id1/data/'+ dirf[0] + '/' + dirf[1] + '/' + dirf[2] + '/' 
    textfilename = 'log_' + fileprefix + '_srx-2dscan-sdd-timeout.py.txt'
    flog=textfiledir+textfilename

    print 'ouput file name:', fileprefix+'_pyxrf.h5'

    fout=foutdir+fileprefix+'_pyxrf.h5'
    fio.xspress3_data_to_hdf(fin, flog, fout)
 

#for (fin, flog, fout) in zip(finList, flogList, foutList): 
#    print fin
#    print flog
#    print fout
