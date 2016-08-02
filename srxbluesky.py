# -*- coding: utf-8 -*-
"""
Created on Tue Feb  2 12:31:29 2016

@author: xf05id1
"""

###callbacks for output xanes text file in energy scan

def texout(header=[], )











###below are obsolete and can be replaced by existing blue sky functions:

def scanresult(header, det=None):  #need to come up a better name

    '''
    provide a scanid and return:
        movaxis = the values of the axis being scanned
        detaxis = the values of the detector of interest
    '''

    h=db[scanid]
    evs = list(get_events(h))
    movaxis = []
    detaxis = []    
    
    mov = evs[0]['descriptor']['run_start']['motors'][0]+'_user_readback'    #getting the scanned axis info, but not working in some scan plan...    
    
    
    for i in range(len(evs)):     
        detaxis.append(evs[i].data[det])
        movaxis.append(evs[i].data[mov])        
    
    if det == None:
        print('must provide which detector object is of interest, e.g. "bpm1_stats_tot1", \
              use "scandatakey" function to find what detectors are available to read.')    
    return movaxis, detaxis
    

def scandatakey(scanid = -1):

    '''
    provide a scanid and return all recorded axis for the scan
    
    '''

    h=db[scanid]
    evs = list(get_events(h))
    
    detlist=[]

    #for key in h['descriptors'][0]['data_keys'].keys():   #alternative
    
    for key in evs[0].data.keys():
        detlist.append(key)

    return detlist
    
