# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 13:47:56 2015

@author: xf05id1
"""
import SRXfileio
import srxdatadir
import os

safnum='300226_Moffet'

beamlineinfo='Data collected at 5ID, SRX beamline, NSLS-II, 2015-3, SAF number:'+str(safnum)    


#convertingdir='/nfs/xf05id1/data/pyxrf_analysis/2015cycle2/huajiang/'
#convertingdir='/nfs/xf05id1/data/pyxrf_analysis/2015cycle2/chonghang/'
convertingdir=srxdatadir.dfpyxrffoutdir+'patchfiles/'

#savingdir = '/nfs/xf05id1/data/SmakFormat/2015cycle2/huajiang/'
#savingdir = '/nfs/xf05id1/data/SmakFormat/2015cycle2/Chonghang/'
##
savingdir = srxdatadir.dfsmakoutdir+'patchfiles/'

filelist=os.listdir(convertingdir)

successlist=[]
faillist=[]
errorlist=[]

for item in filelist:
    print 'working directory:', convertingdir
    if item[-1] != '5':
        print 'not a h5 file:', item
        continue
    else:
        print 'h5 file found:', item
        
#    errorcode, errorcodedef = SRXfileio.PyxrftoSmak(pyxrfdir=convertingdir, infile=item, i0f=1.0, fitdata='det2',
#                          comments=beamlineinfo + ';ion chamber scaling factor = 1.0', filenameadd='i0fsaf', foutdir=savingdir,
#                          noyear = False, notimeout=False)

    errorcode, errorcodedef = SRXfileio.PyxrftoSmak(pyxrfdir=convertingdir, infile=item, i0f=1.0e8, fitdata='det2',
                          comments=beamlineinfo + ';ion chamber scaling factor = 1.0e8', filenameadd='i0f', foutdir=savingdir,
                          noyear = False, notimeout=False, patchfile=False)

    if errorcode == 0:
        successlist.append(item)
    else:
        faillist.append(item)
        errorlist.append(errorcode)


print 'successfully converted file:' 
print 'ok=', successlist
print 'total successful file number = ', len(successlist)
print 'failed file:'
print 'fail=', faillist
print 'errorcode =', errorlist
print 'total failed file number = ', len(errorlist)

print errorcodedef





        