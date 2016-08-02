# -*- coding: utf-8 -*-
"""
Created on Fri Oct 30 13:47:56 2015

@author: xf05id1
"""
import SRXfileio

safnum=300198
fileprefixList=['2015_10_29_20_4',
                '2015_10_29_20_54',
                '2015_10_29_21_58',
                '2015_10_29_22_48',
                '2015_10_30_2_10',
                '2015_10_30_4_4',
                '2015_10_30_4_57',
                '2015_10_30_5_50',
                '2015_10_30_6_43',
                '2015_10_30_8_30',
                '2015_10_30_9_23', 
                '2015_10_30_10_17', #not fitted
                '2015_10_28_21_40',
                '2015_10_28_22_19',
                '2015_10_28_22_58',
                '2015_10_28_23_36',
                '2015_10_29_0_15'
                ]

beamlineinfo='Data collected at 5ID, SRX beamline, NSLS-II, 2015-3, SAF number:'+str(safnum)    




successlist=[]
faillist=[]
errorlist=[]


for item in fileprefixList:
    errorcode, errorcodelist = SRXfileio.PyxrftoSmak(fileprefix=item, i0f=1.0e8, 
                          comments=beamlineinfo + ';ion chamber scaling factor = 1.0e8', filenameadd='i0fsaf')
    if errorcode == 0:
        successlist.append(item)
    else:
        faillist.append(item)
        errorlist.append(errorcode)

print errorcodelist
        