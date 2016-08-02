# -*- coding: utf-8 -*-
"""
Created on Wed Feb 17 13:05:35 2016

@author: xf05id1
"""
from databroker import DataBroker as db, get_table, get_images, get_events
import time

def textout(scan=-1, header=[], userheader={}, column=[], output = True):
    '''
    scan: can be scan_id (integer) or uid (string). defaul = -1 (last scan run)
    '''   
    scanh= db[scan]
    print(scanh.start)
    events=list(get_events(scanh))

 
   #convert time stamp to localtime
    #timestamp=scanhh.start['time']
    #scantime=time.localtime(timestamp)   
    
    filedir='/nfs/xf05id1/userdata/2016cycle2/300265_inhouse/'
    filename='scan_'+ str(scanh.start['scan_id']) 
    f = open(filedir+filename, 'w')

    staticheader = '# XDI/1.0 MX/2.0\n' \
              +'# Beamline.name: '+scanh.start.beamline_id+'\n'  \
              +'# Facility.name: NSLS-II\n'  \
              +'# Scan.start.uid: '+scanh.start.uid+'\n'  \
              +'# Scan.start.time: '+str(scanh.start.time)+'\n'  \
              +'# Scan.start.ctime: '+time.ctime(scanh.start.time)+'\n'  \
              +'# Mono.name: Si 111\n'  \

    f.write(staticheader)

    for item in header:
        if item in events[0].data.keys():
            f.write('# '+item+': '+str(events[0]['data'][item])+'\n')
            if output is True:
                print(item+' is written')
        else: 
            print(item+' is not in the scan')
           
    for key in userheader:
        f.write('# '+key+': '+str(userheader[key])+'\n')
        if output is True:
            print(key+' is written')                   

    for idx, item in enumerate(column): 
        if item in events[0].data.keys():        
            f.write('# Column.'+str(idx+1)+': '+item+'\n')


    f.write('# ') 
    for item in column: 
        if item in events[0].data.keys():        
            f.write(str(item)+'\t')
    f.write('\n')

    for event in events:
        for item in column: 
            if item in events[0].data.keys():        
                f.write(str(event['data'][item])+'\t')
        f.write('\n')
        
    f.close()