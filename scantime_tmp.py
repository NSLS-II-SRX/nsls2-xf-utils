import os
from databroker import DataBroker as db, get_events
import time

def scantime(scanid, printresults=True):
    '''
    input: scanid
    return: start and stop time stamps as strings 
    '''
    start_str = 'scan start: '+time.ctime(db[scanid].start['time'])
    stop_str  = 'scan stop : '+time.ctime(db[scanid].stop['time'])
    totaltime = db[scanid].stop['time'] - db[scanid].start['time']
    scannumpt = len(list(get_events(db[scanid])))
    
    if printresults is True:
        print(start_str)
        print(stop_str)
        print('total time:', totaltime, 's')
        print('number of points:', scannumpt)
        print('scan time per point:', totaltime/scannumpt, 's')
    return db[scanid].start['time'], db[scanid].stop['time'], start_str, stop_str

def timestamp_batchoutput(filename = 'timestamplog.text', initial_scanid = None, final_scanid = None):
    f = open(filename,'w')
    for scanid in range(initial_scanid, final_scanid+1):
        f.write(str(scanid)+'\n')
        try: 
            start_t, stop_t = scantime(scanid)
            f.write(start_t)
            f.write('\n')
            f.write(stop_t)
            f.write('\n')
        except:
            f.write('scan did no finish correctly.\n')
    f.close()

def scantime_batchoutput(filename = 'scantimelog.txt', scanlist = []):

    f = open(filename, 'w')
    f.write('scanid\tstartime(s)\tstoptime(s)\tstartime(date-time)\tstoptime(date-time)\n')
    for i in scanlist:
        starttime_s, endtime_s, starttime, endtime = scantime(i, printresults=False)
        f.write(str(i)+'\t'+str(starttime_s)+'\t'+str(endtime_s)+'\t'+starttime[12::]+'\t'+endtime[12::]+'\n')
    f.close()

