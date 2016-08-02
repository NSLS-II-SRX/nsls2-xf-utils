from __future__ import print_function
import epics
import math
import time
import numpy as np
from matplotlib import pyplot

'''

import xspress3
det=xspress3.nsls2xspress3('XSPRESS3-EXAMPLE')

'''

DET_FIELDS=('Acquire','ERASE','StatusMessage_RBV','ArrayCounter_RBV',\
 'TriggerMode_RBV','TriggerMode','TriggerMode','NumImages_RBV',\
 'NumImages','DetectorState_RBV','CTRL_MCA_ROI','CTRL_MCA_ROI_RBV',\
 'ArrayRate_RBV','Acquire_RBV','CTRL_DTC','CTRL_DTC_RBV','UPDATE',\
 'CONNECTED','AcquireTime_RBV','AcquireTime')
FILE_FIELDS=('FilePath','FilePath_RBV','FilePathExists_RBV',\
 'FileName','FileName_RBV','FileNumber','FileNumber_RBV', 'Capture_RBV',\
 'Capture','NumCaptured_RBV','WriteMessage','WriteStatus')
#ROI_FIELDS=('C1_MCA_ROI1_LLM','C1_MCA_ROI2_LLM','C1_MCA_ROI3_LLM',\
# 'C1_MCA_ROI1_HLM','C1_MCA_ROI2_HLM','C1_MCA_ROI3_HLM',\
# 'C1_ROI1:Value_RBV','C1_ROI2:Value_RBV','C1_ROI3:Value_RBV',\
# 'C1_ROI1:ValueSum_RBV','C1_ROI2:ValueSum_RBV','C1_ROI3:ValueSum_RBV',\
# 'C1_ROI1:ArrayData_RBV','C1_ROI2:ArrayData_RBV','C1_ROI3:ArrayData_RBV')

ROI_FIELDS=('C1_MCA_ROI1_LLM','C1_MCA_ROI2_LLM','C1_MCA_ROI3_LLM', 'C1_MCA_ROI4_LLM', \
 'C1_MCA_ROI1_HLM','C1_MCA_ROI2_HLM','C1_MCA_ROI3_HLM', 'C1_MCA_ROI4_HLM', \
 'C2_MCA_ROI1_LLM','C2_MCA_ROI2_LLM','C2_MCA_ROI3_LLM', 'C2_MCA_ROI4_LLM',\
 'C2_MCA_ROI1_HLM','C2_MCA_ROI2_HLM','C2_MCA_ROI3_HLM', 'C2_MCA_ROI4_HLM'\
 'C3_MCA_ROI1_LLM','C3_MCA_ROI2_LLM','C3_MCA_ROI3_LLM', 'C3_MCA_ROI4_LLM'\
 'C3_MCA_ROI1_HLM','C3_MCA_ROI2_HLM','C3_MCA_ROI3_HLM', 'C3_MCA_ROI4_HLM')

ARRAY_FIELDS=('ArrayData')
#why?  ROI_FIELDS is unused, but the attrs are called out below...
IND_ROI_FIELDS=('Value_RBV', 'ValueSum_RBV','ArrayData_RBV') #individual roi fil

defaultFilePath = '/home/gwilliams/data/'
defaultFileName = 'test'

class nsls2xspress3():
    def __init__(self,prefix):
        self.det=epics.Device(prefix,delim=':',attrs=DET_FIELDS)
        self.h5=epics.Device(prefix+":HDF5",delim=':',attrs=FILE_FIELDS)
        self.roi=epics.Device(prefix,delim=':',attrs=ROI_FIELDS)
        
        self.ch1=epics.Device(prefix+":ARR1",delim=':',attrs=ARRAY_FIELDS)
        self.ch2=epics.Device(prefix+":ARR2",delim=':',attrs=ARRAY_FIELDS) 
        self.ch3=epics.Device(prefix+":ARR3",delim=':',attrs=ARRAY_FIELDS) 
        
        self.ch1sum=epics.Device(prefix+":ARRSUM1",delim=':',attrs=ARRAY_FIELDS)
        self.ch2sum=epics.Device(prefix+":ARRSUM2",delim=':',attrs=ARRAY_FIELDS) 
        self.ch3sum=epics.Device(prefix+":ARRSUM3",delim=':',attrs=ARRAY_FIELDS) 
                       
        self.c1roi1=epics.Device(prefix+":C1_ROI1",delim=':',attrs=IND_ROI_FIELDS)
        self.c1roi2=epics.Device(prefix+":C1_ROI2",delim=':',attrs=IND_ROI_FIELDS)
        self.c1roi3=epics.Device(prefix+":C1_ROI3",delim=':',attrs=IND_ROI_FIELDS)
        self.c1roi4=epics.Device(prefix+":C1_ROI4",delim=':',attrs=IND_ROI_FIELDS)
        
        self.c2roi1=epics.Device(prefix+":C2_ROI1",delim=':',attrs=IND_ROI_FIELDS)
        self.c2roi2=epics.Device(prefix+":C2_ROI2",delim=':',attrs=IND_ROI_FIELDS)
        self.c2roi3=epics.Device(prefix+":C2_ROI3",delim=':',attrs=IND_ROI_FIELDS)
        self.c2roi4=epics.Device(prefix+":C2_ROI4",delim=':',attrs=IND_ROI_FIELDS)
        
        self.c3roi1=epics.Device(prefix+":C3_ROI1",delim=':',attrs=IND_ROI_FIELDS)
        self.c3roi2=epics.Device(prefix+":C3_ROI2",delim=':',attrs=IND_ROI_FIELDS)
        self.c3roi3=epics.Device(prefix+":C3_ROI3",delim=':',attrs=IND_ROI_FIELDS)
        self.c3roi4=epics.Device(prefix+":C3_ROI4",delim=':',attrs=IND_ROI_FIELDS)
                
        self.det.ERASE = 0 #initializing roi data, set them back to zero.
        #why comment this out?
        #self._acqtime = self.det.AcquireTime   
        #self._numframe = self.det.NumImages

#detector        
    def acq(self, erase=True, saveh5 = True, **kwargs):
        '''
        acquire data. 
        keywords:
            erase(default=True: erase all the ROI Integrated values from the previous acqusition and reset them to zeros.
            saveh5(default=True): press 'Start File Saving' before acqusition
        '''
        
        if erase == True:  #reset the roi integrated value to zero from previous acqusition
            self.det.ERASE = 1
            self.det.ERASE = 0            
        
        if saveh5 == True: #saving data into hdf5 files
            self.h5.Capture=1
        
        self.det.put('Acquire',1)
        #if kwargs.has_key('acqtime'):
        #    self.det.AcquireTime=kwargs['acqtime']
        #if kwargs.has_key('numimg'):
        #    self.det.NumImages=kwargs['numimg']
        
    def stop(self):
        '''
        stop the current acqusition
        '''
        #if status is acquire
        self.det.put('Acquire', 0)
            
    def getacqtime(self):
        return self.det.AcquireTime_RBV            
            
    def setacqtime(self, acqtime):
        #self._acqtime = acqtime
        self.det.AcquireTime = acqtime
    
    def getnumframe(self):
        return self.det.NumImages_RBV           
        
    def setnumframe(self, numframe):
        #self._numframe = numframe
        self.det.NumImages = numframe
        
    def getmssg(self):
        statusMssgAscii = self.det.StatusMessage_RBV
        statusMssgText=''.join(chr(i) for i in statusMssgAscii)
        return statusMssgText
        
    def getstatus(self, show=False, **kwargs):
        '''
        return detector status: 1 = Idle, 1 = Acquire, 10 = Aborted, else unknown
        '''        
        detstatus = self.det.DetectorState_RBV
        if show == True:
            if detstatus == 0:
                print('Status: Idle')
            elif detstatus == 1:
                print('Status: Acquire')
            elif detstatus == 10:
                print('Status: Aborted')
            else:              
                print('Status: Unknown')          
        return detstatus
        
    def ready(self, show=False, **kwargs):
        '''
        if the detector is ready (status = idle or aborted), return 1
        otherwise return 0
        keyword: show(default=False): print the detector ready status
        '''
        
        detstatus = self.getstatus()    
        if show == True:
            if detstatus == 0 or detstatus == 10:
                print('Detector is ready.')
            elif detstatus == 1:              
                print('Detector is still acquring.')
            else:
                print('Detector is not ready.')
               
        if detstatus == 0 or detstatus == 10:
            return 1
        else:
            return 0
#hdf5:            
       
    def getfilenum(self):
        '''
        return the current file number attached to the file name'
        '''
        return self.h5.FileNumber_RBV
        
    def setfilenum(self, filenum):       
        '''
        set the file number to be attached to the file name'
        '''
        self.h5.FileNumber = filenum

    def getfile(self):
        '''
        return the current path and file name'
        '''
        h5pathAscii = self.h5.FilePath_RBV
        h5fileAscii = self.h5.FileName_RBV
        h5pathText=''.join(chr(i) for i in h5pathAscii)
        h5fileText=''.join(chr(i) for i in h5fileAscii)

        print('file path:',h5pathText)
        print('file name:',h5fileText+'.hdf5')
        return h5pathText, h5fileText         
        
    def setfile(self, h5path =defaultFilePath, h5name = defaultFileName, resetFilenum = True):
        '''
        set the path and file name'
        keyword: resetFilenum(default=True): reset the file number to 1 when changing the file name
        '''
        self.h5.FilePath = h5path
        self.h5.FileName = h5name
        #need to check if the file path exist

        if resetFilenum == True:       
            self.setfilenum(1)  

    def geth5save(self):
        if self.h5.Capture == 0:
            print('not saving hdf5 file')
        else:
            print('saving hdf5 file')
        return self.h5.Capture            

    def seth5saveon(self):
        self.h5.Capture = 1

    def seth5saveoff(self):
        self.h5.Capture = 0

#entire array:
    
    def getsumarray(self):
        '''
        return a numpy array that is the sum of the cummulative MCA spectra data (from all acquired frames) from all 3 channels
        '''
        sumarray = self.ch1sum.ArrayData + self.ch2sum.ArrayData + self.ch3sum.ArrayData
        return sumarray

    def getchsumarray(self, channel = 1):
        '''
        return a numpy array that is channel specific cummulative MCA spectra data from all acquired frames
        '''        
        if channel == 1:
            return self.ch1sum.ArrayData
        elif channel == 2:
            return self.ch2sum.ArrayData
        elif channel == 3:
            return self.ch3sum.ArrayData
        else:
            print('specify channel 1, 2 or 3')

    def getcharray(self, channel = 1):
        '''
        return a numpy array that is channel specific MCA spectra data from the latest frame
        ''' 
        if channel == 1:
            return self.ch1.ArrayData
        elif channel == 2:
            return self.ch2.ArrayData
        elif channel == 3:
            return self.ch3.ArrayData
        else:
            print('specify channel 1, 2 or 3')
            
#rois:
      
    def setrois(self, roi = 1, llim = 0, hlim = 4096):
        '''
        set the low limit (llim) and high limit (hlim) for the specific roi
        currently roi = 1, 2, 3 or 4
        all 3 channels will use the same roi settings        
        
        '''
        if roi == 1:
            self.roi.C1_MCA_ROI1_LLM = llim
            self.roi.C1_MCA_ROI1_HLM = hlim
            self.roi.C2_MCA_ROI1_LLM = llim
            self.roi.C2_MCA_ROI1_HLM = hlim
            self.roi.C3_MCA_ROI1_LLM = llim
            self.roi.C3_MCA_ROI1_HLM = hlim
        elif roi == 2:
            self.roi.C1_MCA_ROI2_LLM = llim
            self.roi.C1_MCA_ROI2_HLM = hlim
            self.roi.C2_MCA_ROI2_LLM = llim
            self.roi.C2_MCA_ROI2_HLM = hlim
            self.roi.C3_MCA_ROI2_LLM = llim
            self.roi.C3_MCA_ROI2_HLM = hlim            
        elif roi == 3:
            self.roi.C1_MCA_ROI3_LLM = llim
            self.roi.C1_MCA_ROI3_HLM = hlim
            self.roi.C2_MCA_ROI3_LLM = llim
            self.roi.C2_MCA_ROI3_HLM = hlim
            self.roi.C3_MCA_ROI3_LLM = llim
            self.roi.C3_MCA_ROI3_HLM = hlim
        elif roi == 4:
            self.roi.C1_MCA_ROI4_LLM = llim
            self.roi.C1_MCA_ROI4_HLM = hlim
            self.roi.C2_MCA_ROI4_LLM = llim
            self.roi.C2_MCA_ROI4_HLM = hlim
            self.roi.C3_MCA_ROI4_LLM = llim
            self.roi.C3_MCA_ROI4_HLM = hlim
        else:
            print('please specify the right roi')
    
    def setroioff(self, roi = 4):
        '''
        set the selected roi low limit and high limit both to zeros
        '''
        self.setrois(self, roi = roi, llim = 0, hlim = 0)

    def setchrois(self, channel = 1, roi = 1, llim = 0, hlim = 4096):
        '''
        set the low limit (llim) and high limit (hlim) for the specific roi, for the specific channel
        currently roi = 1, 2, 3 or 4
        '''
        if channel == 1:
            if roi == 1:
                self.roi.C1_MCA_ROI1_LLM = llim
                self.roi.C1_MCA_ROI1_HLM = hlim
            elif roi == 2:
                self.roi.C1_MCA_ROI2_LLM = llim
                self.roi.C1_MCA_ROI2_HLM = hlim
            elif roi == 3:
                self.roi.C1_MCA_ROI3_LLM = llim
                self.roi.C1_MCA_ROI3_HLM = hlim
            elif roi == 4:
                self.roi.C1_MCA_ROI4_LLM = llim
                self.roi.C1_MCA_ROI4_HLM = hlim
            else:
                print('please specify the right roi')
        elif channel == 2:
            if roi == 1:
                self.roi.C2_MCA_ROI1_LLM = llim
                self.roi.C2_MCA_ROI1_HLM = hlim
            elif roi == 2:
                self.roi.C2_MCA_ROI2_LLM = llim
                self.roi.C2_MCA_ROI2_HLM = hlim
            elif roi == 3:
                self.roi.C2_MCA_ROI3_LLM = llim
                self.roi.C2_MCA_ROI3_HLM = hlim
            elif roi == 4:
                self.roi.C2_MCA_ROI4_LLM = llim
                self.roi.C2_MCA_ROI4_HLM = hlim                
            else:
                print('please specify the right roi')               
        elif channel == 3:
            if roi == 1:
                self.roi.C3_MCA_ROI1_LLM = llim
                self.roi.C3_MCA_ROI1_HLM = hlim
            elif roi == 2:
                self.roi.C3_MCA_ROI2_LLM = llim
                self.roi.C3_MCA_ROI2_HLM = hlim
            elif roi == 3:
                self.roi.C3_MCA_ROI3_LLM = llim
                self.roi.C3_MCA_ROI3_HLM = hlim
            elif roi == 4:
                self.roi.C3_MCA_ROI4_LLM = llim
                self.roi.C3_MCA_ROI4_HLM = hlim  
            else:
                print('please specify the right roi')
        else:
            print('specify channel 1, 2 or 3')      
            
    def getchrois(self, channel = 1, roi = 1):
        '''
        return a numpy array array[llim, hlim]: the low limit (llim) and high limit (hlim) for the specific roi, for the specific channel
        currently roi = 1, 2, 3 or 4
        '''
        if channel == 1:
            if roi == 1:
                llim = self.roi.C1_MCA_ROI1_LLM
                hlim = self.roi.C1_MCA_ROI1_HLM
            elif roi == 2:
                llim = self.roi.C1_MCA_ROI2_LLM
                hlim = self.roi.C1_MCA_ROI2_HLM
            elif roi == 3:
                llim = self.roi.C1_MCA_ROI3_LLM
                hlim = self.roi.C1_MCA_ROI3_HLM
            elif roi == 4:
                llim = self.roi.C1_MCA_ROI4_LLM
                hlim = self.roi.C1_MCA_ROI4_HLM
            else:
                print('please specify the right roi')
        elif channel == 2:
            if roi == 1:
                llim = self.roi.C2_MCA_ROI1_LLM
                hlim = self.roi.C2_MCA_ROI1_HLM
            elif roi == 2:
                llim = self.roi.C2_MCA_ROI2_LLM
                hlim = self.roi.C2_MCA_ROI2_HLM
            elif roi == 3:
                llim = self.roi.C2_MCA_ROI3_LLM
                hlim = self.roi.C2_MCA_ROI3_HLM
            elif roi == 4:
                llim = self.roi.C2_MCA_ROI4_LLM
                hlim = self.roi.C2_MCA_ROI4_HLM                
            else:
                print('please specify the right roi')               
        elif channel == 3:
            if roi == 1:
                llim = self.roi.C3_MCA_ROI1_LLM
                hlim = self.roi.C3_MCA_ROI1_HLM
            elif roi == 2:
                llim = self.roi.C3_MCA_ROI2_LLM
                hlim = self.roi.C3_MCA_ROI2_HLM
            elif roi == 3:
                llim = self.roi.C3_MCA_ROI3_LLM
                hlim = self.roi.C3_MCA_ROI3_HLM
            elif roi == 4:
                llim = self.roi.C3_MCA_ROI4_LLM
                hlim = self.roi.C3_MCA_ROI4_HLM  
            else:
                print('please specify the right roi')
        else:
            print('specify channel 1, 2 or 3')     
        return np.array([llim, hlim])           

    def getroivalue(self, roi = 1):
        '''
        for specific roi, return two variables:
            roisum: a single value that is the sum of the integrated ROI readback value of all 3 channels
            roich: a numpy array that contains the integrated ROI readback value of all 3 channels
        currently roi = 1, 2, 3 or 4
        '''
        roich=[]  #save roi vallue for each channel
        roisum=0.
       
        if roi == 1:
            roich.append(self.c1roi1.ValueSum_RBV)
            roich.append(self.c2roi1.ValueSum_RBV)
            roich.append(self.c3roi1.ValueSum_RBV)
        elif roi == 2:
            roich.append(self.c1roi2.ValueSum_RBV)
            roich.append(self.c2roi2.ValueSum_RBV)
            roich.append(self.c3roi2.ValueSum_RBV)          
        elif roi == 3:
            roich.append(self.c1roi3.ValueSum_RBV)
            roich.append(self.c2roi3.ValueSum_RBV)
            roich.append(self.c3roi3.ValueSum_RBV)
        elif roi == 4:
            roich.append(self.c1roi4.ValueSum_RBV)
            roich.append(self.c2roi4.ValueSum_RBV)
            roich.append(self.c3roi4.ValueSum_RBV) 
        else:
            print('please specify the right roi') 
        
        roisum=sum(roich)
        return roisum, np.array(roich)
    
    def getallroisum(self):
        '''
        return a numpy array that contains an array of the sum of the integrated ROI readback value of all 3 channels from all 4 rois
        e.g. 
        test=xspress3.nsls2xspress3('XSPRESS3-EXAMPLE')      
        roisumlist = test.getallroisum
        roisumlist[0] is all 3 channels sum of the integrated ROI readback from roi1
        roisumlist[1] is all 3 channels sum of the integrated ROI readback from roi2
        roisumlist[2] is all 3 channels sum of the integrated ROI readback from roi3        
        roisumlist[3] is all 3 channels sum of the integrated ROI readback from roi4
        
        '''
        roisumlist = []
        for i in range(1,5):
            roisum, roich = self.getroivalue(roi = i)
            roisumlist.append(roisum)
        return np.array(roisumlist)

    def plotchsum(self, channel = 1):
        '''
        a simple plotting funtion that plots the result from getcharray for a specific channel
        '''
        if channel == 1:
            ch = self.getcharray(channel=1)
        elif channel == 2:
            ch = self.getcharray(channel=2)
        elif channel == 3:
            ch = self.getcharray(channel=3)
        else:
            print('specify channel 1, 2 or 3')
            
        xaxis = range(0,4096)
        p = pyplot.plot(xaxis, ch)
        pyplot.show(p)    
    
#acquire time, numframe
#

#.ready: check detector status
# export epics ndarray to nparray
#turn on/off rois
#filename, path
