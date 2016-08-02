# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 17:22:39 2015
1. load a set of XRF 2D data, which were collected as a function of time
2. for each file, read from the text file to obtain 1) energy and 2) i0
3. flip x direction for every other raw
4. output to Data Exchange stac format 


@author: xf05id1
"""

import string
import sys
import srxdatadir
import numpy
import h5py

#dfx3filedir = '/data/XSPRESS3/2015-3/in-house/'
#dfpyxrffoutdir='/nfs/xf05id1/data/pyxrf_analysis/unsorted/'


def flipevenrows(inArray):

    outArray = inArray
    datadim = len(inArray.shape)

    if datadim == 2:
        ydim,xdim = inArray.shape
        for row in xrange(1,ydim, 2):
            outArray[row,:] = inArray[row,-1::-1]
    elif datadim == 3:
        ydim,xdim, mcach = inArray.shape
        for row in xrange(1,ydim, 2):
            outArray[row,:, :] = inArray[row,-1::-1, :]
    else:
        print 'data dimension must be 2 or 3'
    
    return outArray

def readtextlog2dscan(fileprefix=None, scriptversion='sdd-timeout', noyear = False):
    dirf = string.split(fileprefix, sep='_')
    textfiledir = '/nfs/xf05id1/data/'+ dirf[0] + '/' + dirf[1] + '/' + dirf[2] + '/'     

    linetoskip = 3
    linetoskipPost = 2
    
    scantype='2dscan'
    if noyear == True:
        fileprefix = fileprefix[5::]       
   
    textfilename = 'log_' + fileprefix + '_srx-' + scantype + '-' + scriptversion +'.py.txt'
    logfile=textfiledir+textfilename    
       
    ptnumList = []
    xList = []
    yList = []
    i0List = []
    
    argDict={}
        
    flog = open(logfile, 'r')    

    #parse the first line to obtain the necessary information
    line=flog.readline()
    line=line.replace(', --', ' ')
    argumentList=line.split(' ')
    
    for i in argumentList:
        if '=' in i:
            argDict[i.split('=')[0]]=i.split('=')[1]
            
    for j in xrange(linetoskip+1):
        line=flog.readline()
        print j
        print line
        
    line=flog.readline()
    line=line.replace(';', ':')
    energyline=string.split(line, sep = ':')
    k=0
    for i in energyline:
        if i == ' Energy':
            energy=energyline[k+1]
            print 'energy was:', energy
            break
        k=k+1       
  
    for j in xrange(linetoskipPost+1):
        line=flog.readline()
        print j
        print line              
    
    flag = False
    while line[0] != '#':          
       linefields=string.split(line, sep = ' ')
       linefields = [validitem for validitem in linefields if validitem]
       ptnumList.append(int(linefields[0]))
       xList.append(float(linefields[1]))
       yList.append(float(linefields[2]))
       if flag == True:
           i0List.append(float(linefields[4]))
           flag = False
       if  float(linefields[4]) == 0:
           flag = True
       else:
           i0List.append(float(linefields[4]))       
    
       line=flog.readline()
       
    print 'last line read:'
    print line

    i0List=numpy.array(i0List)

    for item in argDict:
        if item == 'xnumstep' or item == 'ynumstep' or item == 'acqnum':
            argDict[item] = int(argDict[item])
        elif item == 'detname':
            continue
        else:
            argDict[item] = float(argDict[item])

    if line[0:4] == '#End':
        print 'read all the points, scan finished correctly'
        ydim = argDict['ynumstep']+1
        xdim = argDict['xnumstep']+1
        print '(y,x) dimension = '+ str(ydim) + ',' + str(xdim)
        ptnumList = numpy.reshape(ptnumList, [ydim, xdim])
        xListraw=xList
        yListraw=yList
        xList = numpy.reshape(xList,  [ydim, xdim])
        yList = numpy.reshape(yList,  [ydim, xdim])
        i0List = numpy.reshape(i0List,  [ydim, xdim])

    #flip all even rows
        ptnumList=flipevenrows(ptnumList)
        xList=flipevenrows(xList)
        yList=flipevenrows(yList)
        i0List=flipevenrows(i0List)
                
        return argDict, ydim, xdim, ptnumList, xList, yList, i0List, xListraw, yListraw, energy
    else:
       print line
       print 'Incomplete log file.'
       
    flog.close()

def writeh5py(foutname, xvals, yvals, xanesstackdata, energyList): 
        
    fout = h5py.File(foutname, 'w') 
    exchangegrp = fout.create_group('/exchange') 
    fout.create_dataset('implements', data='information:exchange:spectromicroscopy') 
    fout.create_dataset('version', data='1.0') 

  
    #save the final x,y position to pyxrf.h5
    if xvals != None and yvals != None:    
        print 'writing x,y position'
        exchangegrp.create_dataset('x', data=numpy.transpose(xvals[0,:][numpy.newaxis]))
        exchangegrp.create_dataset('y', data=numpy.transpose(yvals[:,0][numpy.newaxis]))
    else:
        print 'x,y positions missing'    
    
    #save the final detector mca values to pyxrf.h5
    
    if xanesstackdata != None:
        print 'writing xanes stack data'
        dataset_data= exchangegrp.create_dataset('data', data=xanesstackdata)
        dataset_data.attrs['axes'] = 'y:x:energy'
        dataset_data.attrs['signal'] = 1
    else:
        print 'xanes stack data missing' 

    if energyList != None:
        print 'energy'      
        dataset_energy = exchangegrp.create_dataset('energy', data=energyList)
        dataset_energy.attrs['units'] = 'ev'
    else:
        print 'energy missing'
            
    fout.close()
    return 0


def x3toDataExchange(x3dir=srxdatadir.dfx3filedir, fileprefixList=None, foutdir=srxdatadir.dfxanesstackoutdir, filenum=0,
              scriptversion='sdd-timeout', noyear = False, stage='nPoint', missingpt = False, filepost = '', datach = 'ch1',
              roil=None, roih=None, divbyi0 = True,
              writefile=True):

    '''
    Example: 
     x3toPyxrf(x3dir='/data/XSPRESS3/2015-3/300226/', fileprefix='2015_11_12_14_46', foutdir='/nfs/xf05id1/data/pyxrf_analysis/2015cycle3/300226_Hesterberg/', filenum=0,
              scriptversion='sdd-timeout', noyear = False, stage='nPoint', missingpt = True, filepost = 'test', datach = 'chsum',
              roil = 1000, roil = 1025
               writefile=True)

    datach = 'ch1', 'ch2', 'ch3', or 'chsum'
    roil and roih can be checked by x3plot.xrfxanescheck module
    
    ''' 

    enum = 0
    for fileprefix in fileprefixList:


        i0baseval = 8.5*1e-10
    
        print 'input file directory:', foutdir
    
        detelenum = 3
        if fileprefix == None:
            print "please provide a fileprefix as indicated in Xspress3 screen. E.g. '2015_10_25_21_14'"
            sys.exit()
       
        if fileprefix[-1] == '_':
            fileprefix=fileprefix[0:-1]
    
        #read the text log file: 
        print 'read i0 data and scanning motor positions from text log file...'
        argDict, ydim, xdim, ptnumList, xList, yList, i0List, xListraw, yListraw, energy = readtextlog2dscan(fileprefix=fileprefix, scriptversion=scriptversion, noyear = noyear)
      
        finname=x3dir+fileprefix+'_'+str(filenum)+'.hdf5'  #X3 data
        print 'reading:', finname
        
        #finname=findir+fileprefix+'_pyxrf.h5' #for future, adding pyxrf format?
        if missingpt == True:
            foutname=foutdir+fileprefix+'_'+filepost+'_fixmissingpt_pyxrf.hdf5'#pyXRFdata with missing pont fixed
        else:
            foutname=foutdir+fileprefix+'_'+filepost+'_dataexchange.hdf5'#pyXRFdata
     
        fin = h5py.File(finname, 'r') 
             
        #read the data from the detector
        print 'reading position data from detector hdf5 file'
        if stage =='nPoint':
            xvals = numpy.array(fin['/entry/instrument/NDAttributes/NpointX'])
            yvals = numpy.array(fin['/entry/instrument/NDAttributes/NpointY'])
        
        else:
            print 'not yet considering these stages'    
    
        print 'reading mca data from detector hdf5 file'
        mcadata = numpy.array(fin['/entry/instrument/detector/data'])        

        #return xvals, yvals, mcadata

        fin.close()         
        
        print 'detector data shape:', mcadata.shape    
        [ysize, xsize, frame, detele, cha] = mcadata.shape   
    
        if frame == 1:
            mcadata = numpy.reshape(mcadata, [ydim, xdim, detele, cha])
            
    
        else:
            print 'more than one frame was collected per point... not sure what to do yet...'
            sys.exit()
                     
        #reshape and flip arrays    
        xvals = numpy.reshape(xvals,  [ydim, xdim])
        yvals = numpy.reshape(yvals,  [ydim, xdim])
        xvals = flipevenrows(xvals)
        yvals = flipevenrows(yvals)
        mcadata = numpy.reshape(mcadata, [ydim, xdim, detele, cha])
        
        if datach == 'ch1':
            readdata = numpy.array(mcadata[:,:,0,:])
        elif datach == 'ch2':
            readdata = numpy.array(mcadata[:,:,1,:])
        elif datach == 'ch3':
            readdata = numpy.array(mcadata[:,:,2,:])
        elif datach == 'chsum':
            readdata=numpy.zeros((ydim, xdim, cha))
            for i in range(detele):
                readdata=readdata+mcadata[:,:,i,:]
    
        readdata = flipevenrows(readdata)
    
        if fileprefix == fileprefixList[0]:
            xanesstackdata = numpy.zeros([ydim, xdim, len(fileprefixList)])
            energyList=[]
        xanesstackdata[:,:,enum] = numpy.sum(readdata[:,:,roil:roih], axis=2)       
        if divbyi0 == True:
            xanesstackdata[:,:,enum] = xanesstackdata[:,:,enum]/numpy.abs((i0List-i0baseval)/1.0e8)
        else:
            xanesstackdata[:,:,enum] = xanesstackdata[:,:,enum]

        enum = enum+1
        energyList.append(float(energy))


    energyList=numpy.array(energyList)          
    if writefile == True:
        print 'writing pyxrf file...'
        err = writeh5py(foutname, xvals, yvals, xanesstackdata, energyList)               
               
    return xdim, ydim, xsize, ysize, xvals, yvals, i0List, detelenum, xanesstackdata
    