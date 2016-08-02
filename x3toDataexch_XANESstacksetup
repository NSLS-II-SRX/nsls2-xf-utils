# -*- coding: utf-8 -*-
"""
Created on Mon Aug 24 17:22:39 2015

@author: xf05id1
"""

import string
import sys
import srxdatadir
import numpy
import h5py

#dfx3filedir = '/data/XSPRESS3/2015-3/in-house/'
#dfpyxrffoutdir='/nfs/xf05id1/data/pyxrf_analysis/unsorted/'

##rewrite to:
    ##1. implmeneting everything from scratch
    ##2. handle missing point when specified
    ##3. run stitching when specified

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

    linetoskip = 7
    
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
        #print j
        #print line
    
    while line[0] != '#':          
       linefields=string.split(line, sep = ' ')
       linefields = [validitem for validitem in linefields if validitem]
       ptnumList.append(int(linefields[0]))
       xList.append(float(linefields[1]))
       yList.append(float(linefields[2]))
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
                
        return argDict, ydim, xdim, ptnumList, xList, yList, i0List, xListraw, yListraw
    else:
       print line
       print 'Incomplete log file.'
       
    flog.close()

def writeh5py(foutname, i0Array, i0baseval, xvals, yvals, mcadata, summca, detelenum, ch1mca, ch2mca, ch3mca): 
        
    fout = h5py.File(foutname, 'w') 

    i0Array = numpy.reshape(i0Array,  [i0Array.shape[0], i0Array.shape[1], 1])

    if i0Array != None:     
        print 'write i0 to pyxrf h5 file...'
        #read and write the i0 data        
        scalergrp = fout.create_group('/xrfmap/scalers') 
        scalergrp.create_dataset('name', data=['scalers_ch2'])
        scalergrp.create_dataset('val', data=numpy.abs(i0Array-i0baseval))
    else:
        print 'skipping i0'
    
    
    #save the final x,y position to pyxrf.h5
    if xvals != None and yvals != None:    
        print 'writing x,y position'
        positiongrp = fout.create_group('/xrfmap/positions') 
        positiongrp.create_dataset('name', data=['x_pos', 'y_pos'])
        positiongrp.create_dataset('pos', data=[xvals, yvals])
    else:
        print 'skipping x,y positions'    
    
    #save the final detector mca values to pyxrf.h5
    
    if mcadata != None:
        print 'writing mca data'
        detchgrp=[]
        for i in range(detelenum):
            detchgrp.append(fout.create_group('/xrfmap/det'+str(i+1)))
        print 'detchgrpshaep:'+str(len(detchgrp))                  
        
        for i in range(detelenum):
            detgrp=detchgrp[i]
            chdata=detgrp.create_dataset('counts', data=mcadata[:,:,i,:])
            chdata.attrs['comments'] = 'Experimental data from channel ' + str(i)
    else:
        print 'skipping mcadata' 

    if summca != None:
        print 'writing summca data'
        chmcagrp = fout.create_group('/xrfmap/detsum') 
        chdata=chmcagrp.create_dataset('counts', data=summca)
        chdata.attrs['comments'] = 'Experimental data from channel sum'
        
    else:
        print 'skipping summca' 

    if ch1mca != None:
        print 'writing ch1 mca'
        chmcagrp=fout.create_group('/xrfmap/det1')        
        chdata=chmcagrp.create_dataset('counts', data=ch1mca)
        chdata.attrs['comments'] = 'Experimental data from channel 1'
    else:
        print 'skipping individual ch1 mca' 

    if ch2mca != None:
        print 'writing ch2 mca'
        chmcagrp=fout.create_group('/xrfmap/det2')        
        chdata=chmcagrp.create_dataset('counts', data=ch2mca)
        chdata.attrs['comments'] = 'Experimental data from channel 2'
    else:
        print 'skipping individual ch2 mca' 

    if ch3mca != None:
        print 'writing ch3 mca'
        chmcagrp=fout.create_group('/xrfmap/det3')        
        chdata=chmcagrp.create_dataset('counts', data=ch3mca)
        chdata.attrs['comments'] = 'Experimental data from channel 3'
    else:
        print 'skipping individual ch3 mca' 
    
    fout.close()
    return 0


def x3toPyxrf(x3dir=srxdatadir.dfx3filedir, fileprefix=None, foutdir=srxdatadir.dfpyxrffoutdir, filenum=0,
              scriptversion='sdd-timeout', noyear = False, stage='nPoint', missingpt = False, filepost = '',
              writefile=True):

    '''
    Example: 
     x3toPyxrf(x3dir='/data/XSPRESS3/2015-3/300226/', fileprefix='2015_11_12_14_46', foutdir='/nfs/xf05id1/data/pyxrf_analysis/2015cycle3/300226_Hesterberg/', filenum=0,
              scriptversion='sdd-timeout', noyear = False, stage='nPoint', missingpt = True, filepost = 'test',
               writefile=True)
    '''

    i0baseval = 8.5*1e-10
    ch1mca = ch2mca = ch3mca = None

    print 'input file directory:', foutdir

    detelenum = 3
    if fileprefix == None:
        print "please provide a fileprefix as indicated in Xspress3 screen. E.g. '2015_10_25_21_14'"
        sys.exit()
   
    if fileprefix[-1] == '_':
        fileprefix=fileprefix[0:-1]

    #read the text log file: 
    print 'read i0 data and scanning motor positions from text log file...'
    argDict, ydim, xdim, ptnumArray, xArray, yArray, i0Array, xArrayraw, yArrayraw = readtextlog2dscan(fileprefix=fileprefix, scriptversion=scriptversion)
  
    finname=x3dir+fileprefix+'_'+str(filenum)+'.hdf5'  #X3 data
    #finname=findir+fileprefix+'_pyxrf.h5' #for future, adding pyxrf format?
    if missingpt == True:
        foutname=foutdir+fileprefix+'_'+filepost+'_fixmissingpt_pyxrf.h5'#pyXRFdata with missing pont fixed
    else:
        foutname=foutdir+fileprefix+'_'+filepost+'_pyxrf.h5'#pyXRFdata
 
    fin = h5py.File(finname, 'r') 
         
    #read the data from the detector
    print 'reading position data from detector hdf5 file'
    if stage =='nPoint':
        xvals = numpy.array(fin['/entry/instrument/NDAttributes/NpointX'])
        yvals = numpy.array(fin['/entry/instrument/NDAttributes/NpointY'])

    else:
        print 'not yet considering these stages'    

    print 'reading mca data from detector hdf5 file'
    mcadata = fin['/entry/instrument/detector/data']  
    
    print 'detector data shape:', mcadata.shape    
    [ysize, xsize, frame, detele, cha] = mcadata.shape   

    #ch1mca = numpy.array(mcadata[:,:,:,0,:])
    #ch2mca = numpy.array(mcadata[:,:,:,1,:])
    #ch3mca = numpy.array(mcadata[:,:,:,2,:])
    #summca = ch1mca+ch2mca+ch3mca  

    if frame == 1:
        mcadata = numpy.reshape(mcadata, [ydim, xdim, detele, cha])
        summca=numpy.zeros((ydim, xdim, cha))

    else:
        print 'more than one frame was collected per point... not sure what to do yet...'
        sys.exit()
         
    if missingpt == True:
        print 'fix the missing pixel in detector hdf5.'

        for misspt in xrange(len(xvals)):
            #compare the coordinates between the text file and the detector
            if (xvals[misspt] - xArrayraw[misspt]) >= 0.1 or (yvals[misspt] - yArrayraw[misspt]) >= 0.1:
                missx = xvals[misspt]
                missy = yvals[misspt]
                print 'missing point #' + str(misspt) + '; at :' + str(missx) + ',' + str(missy) + '; should be :' + str(xArrayraw[misspt]) + ',' + str(yArrayraw[misspt])
                
                #fix the missing points by shifteverything by one pixel at misspt 

                [yind, xind] = numpy.unravel_index(misspt, (ydim,xdim))
                print 'yind, xind:', yind, xind
                flatinIndex=[]
                flatdelIndex=[]
                for i in range(detele):
                    flatinIndex.append (numpy.ravel_multi_index((yind,xind,i, 0), dims=mcadata.shape))
                    flatdelIndex.append(numpy.ravel_multi_index((ydim-1,xdim-1,i, 0), dims=mcadata.shape)+4096)
                #ch1flatin = numpy.ravel_multi_index((yind,xind,0, 0), dims=mcadata.shape)
                #ch2flatin = numpy.ravel_multi_index((yind,xind,1, 0), dims=mcadata.shape)
                #ch3flatin = numpy.ravel_multi_index((yind,xind,2, 0), dims=mcadata.shape)
                
                print 'flatinIndex:', flatinIndex
                print 'flatdelIndex:', flatdelIndex
                mcadata=mcadata.flatten()
                
                print 'mcadata shape =',  mcadata.shape

                for i in range(detele):
                    mcadata=numpy.insert(mcadata, flatinIndex[i], numpy.zeros(4096))
                    mcadata=numpy.delete(mcadata, numpy.s_[flatdelIndex[i]:flatdelIndex[i]+4096] )
                #mcadata=numpy.insert(range(4096), ch1flatin, mcadata)
                #mcadata=numpy.insert(range(4096), ch2flatin, mcadata)
                #mcadata=numpy.insert(range(4096), ch3flatin, mcadata)
                
                xvals=numpy.insert(xvals, misspt, xArrayraw[misspt])
                yvals=numpy.insert(yvals, misspt, yArrayraw[misspt])                                 
                xvals=numpy.delete(xvals, -1)
                yvals=numpy.delete(yvals, -1)               
                                                         
        #return xvals, yvals, mcadata, xArrayraw, yArrayraw, misspt, ysize, xsize          
                #break      
         
    #reshape and flip arrays    
    xvals = numpy.reshape(xvals,  [ydim, xdim])
    yvals = numpy.reshape(yvals,  [ydim, xdim])
    xvals=flipevenrows(xvals)
    yvals=flipevenrows(yvals)


    mcadata = numpy.reshape(mcadata, [ydim, xdim, detele, cha])
    
    for i in range(detele):
        mcadata[:,:,i,:]=flipevenrows(mcadata[:,:,i,:])
        summca=summca+mcadata[:,:,i,:]
#        ch1mca = numpy.array(mcadata[:,:,0,:])
#        ch2mca = numpy.array(mcadata[:,:,1,:])
#        ch3mca = numpy.array(mcadata[:,:,2,:])
#        summca = ch1mca+ch2mca+ch3mca   

    fin.close() 
    
    if writefile == True:
        print 'writing pyxrf file...'

        err = writeh5py(foutname, i0Array, i0baseval, xvals, yvals, mcadata, summca, detelenum, ch1mca, ch2mca, ch3mca)
       
        
#        fout = h5py.File(foutname, 'w') 
# 
#        print 'write i0 to pyxrf h5 file...'
#        #read and write the i0 data
#
#
#        scalergrp = fout.create_group('/xrfmap/scalers') 
#        scalergrp.create_dataset('name', data='scalers_ch2')
#        scalergrp.create_dataset('val', data=numpy.abs(i0Array-i0baseval))
#
#        
#        #save the final x,y position to pyxrf.h5
#        print 'writing x,y position'
#        positiongrp = fout.create_group('/xrfmap/positions') 
#        positiongrp.create_dataset('name', data=['x_pos', 'y_pos'])
#        positiongrp.create_dataset('pos', data=[xvals, yvals])
#        
#    
#        #save the final detector mca values to pyxrf.h5
#        print 'writing mca data'
#        detchgrp=[]
#        for i in range(detelenum):
#            detchgrp.append(fout.create_group('/xrfmap/det'+str(i+1)))
#        print 'detchgrpshaep:'+str(len(detchgrp))                  
#        detsumgrp = fout.create_group('/xrfmap/detsum') 
#
#        for i in range(detele):
#            detgrp=detchgrp[i]
#            detgrp.create_dataset('counts', data=mcadata[:,:,i,:])
#        detsumgrp.create_dataset('counts', data=summca)
#        
#        fout.close()  
        
    return mcadata, summca, xdim, ydim, xsize, ysize, xvals, yvals, i0Array, detelenum, cha   
    

def PyxrfPatch(fileprefixList=[None], patchingsizex= None, patchingsizey=None,
              x3dir=srxdatadir.dfx3filedir, foutdir=srxdatadir.dfpyxrffoutdir, filenum=0,
              filenameprefix=None, patchch='all', fastaxis='x', coarsexmove = None,
              scriptversion='sdd-timeout', noyear = False, stage='nPoint', missingpt = False, filepost = ''):

    i0baseval = 8.5*1e-10
    patchch = str(patchch)    
                                
    if len(fileprefixList) != (patchingsizex*patchingsizey):
        print 'the nubmer of file size and the patchingsize do not match'
        return    
    
    if filenameprefix == None:
        filenameprefix = fileprefixList[0]
    print 'patching all files into one file based on x,y positions.'


    filecount = 0

    foutname=foutdir+filenameprefix+'_ch'+patchch+'patch_pyxrf.h5'#pyXRFdata with missing pont fixed 
   
    firstdata=True
 
    i0Array=None
    xvals=None
    yvals=None
    mcadata=None
    summca=None
    ch1mca=None
    ch2mca=None
    ch3mca=None

    if fastaxis == 'x':
        fastaxissize=patchingsizex
        slowaxissize=patchingsizey
    elif fastaxis == 'y':
        slowaxissize=patchingsizex
        fastaxissize=patchingsizey   
    else:
        print "fastaxis must = 'x' or 'y'"

    print 'fastaxissize='+str(fastaxissize)
    print 'slowaxissize='+str(slowaxissize)
    
    for slow in xrange(slowaxissize):
        for fast in xrange(fastaxissize):
            
            if fastaxis == 'x':  
                i=fast
                j=slow
            else:
                i=slow
                j=fast
            
            fileprefixnow=fileprefixList[filecount]

            print fileprefixnow
        
            print 'read i0 data and scanning motor positions from text log file...'
            mcadata0, summca0, xdim0, ydim0, xsize0, ysize0, xvals0, yvals0, i0Array0, detelenum, cha= x3toPyxrf(
                  x3dir=x3dir, fileprefix=fileprefixnow, foutdir=foutdir, filenum=0,
                  scriptversion=scriptversion, noyear = noyear, stage=stage, 
                  missingpt = missingpt, filepost = filepost,
                  writefile=False)
            print xdim0
            print ydim0
            
            
            if coarsexmove != None:
                coarsexmove = numpy.array(coarsexmove)
                xvals0 = xvals0 - coarsexmove[filecount]
           
            if firstdata == True:
                  i0Array=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex))                  
                  xvals=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex))
                  yvals=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex))
                  
                  if patchch == 'all':
                      summca=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex, cha))
                      ch1mca=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex, cha))
                      ch2mca=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex, cha))
                      ch3mca=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex, cha))
                  elif patchch == 'sum':
                      summca=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex, cha))
                  elif patchch == '1':
                      ch1mca=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex, cha))
                  elif patchch == '2':
                      ch2mca=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex, cha))
                  elif patchch == '3':
                      ch3mca=numpy.zeros((ydim0*patchingsizey, xdim0*patchingsizex, cha))
                  else:     
                      print 'patchch must = 1, 2, 3, or sum'
                      return
                  print 'initial array size =' + str(ydim0*patchingsizey) + ',' + str(xdim0*patchingsizex)
                  #mcadata=numpy.zeros((xdim0*patchingsizex, ydim0*patchingsizey, detelenum, cha)) 
                  firstdata = False
                  print firstdata
    
    
            print firstdata
            print 'smal array index range, y=' + str(j*ydim0) + ':' + str((j+1)*ydim0) + ';x=' + str(i*xdim0) + ':'+ str((i+1)*xdim0)
            i0Array[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0] = i0Array0
            xvals[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0] = xvals0
            yvals[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0] = yvals0
            
            if patchch == 'all':
                summca[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, :] = summca0
                ch1mca[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, :] = mcadata0[:,:,0,:]
                ch2mca[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, :] = mcadata0[:,:,1,:]
                ch3mca[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, :] = mcadata0[:,:,2,:]
            elif patchch == 'sum':
                summca[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, :] = summca0
            elif patchch == '1':            
                ch1mca[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, :] = mcadata0[:,:,0,:]
            elif patchch == '2':
                ch2mca[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, :] = mcadata0[:,:,1,:]
            elif patchch == '3':
                ch3mca[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, :] = mcadata0[:,:,2,:]
            #for k in range(detelenum):
            #    mcadata[j*ydim0:(j+1)*ydim0, i*xdim0:(i+1)*xdim0, k, :] = mcadata0[:,:,k, :]            

            filecount=filecount+1

    print 'patching channel = ' + patchch

           
    writeh5py(foutname, i0Array, i0baseval, xvals, yvals, mcadata, summca, detelenum, ch1mca, ch2mca, ch3mca)
    #return xvals
        
    #fio.xspress3_data_to_hdf(fin, flog, fout)
 

#for (fin, flog, fout) in zip(finList, flogList, foutList): 
#    print fin
#    print flog
#    print fout
