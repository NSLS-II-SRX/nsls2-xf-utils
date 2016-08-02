import h5py
import matplotlib.pyplot as plt
import numpy
import string
import PIL
import os
import sys
import srxdatadir

##### for loading HDF5 from Xspress3 

def checkfile(filedir, filename):
    ifdirdir = os.path.isdir(filedir)    
    ifdirexist = os.path.exists(filedir)    
    iffileexist = os.path.exists(filedir+filename)       
    
    return ifdirdir, ifdirexist, iffileexist



##########to-do
##ADD srxdatadir.dfx3filedirfix

def x3missing(pyxrfdir=srxdatadir.dfx3filedir, infile=None, fileprefix=None, foutdir=srxdatadir.dfx3filedirfix, filenum=0, comments = '', i0f=1.0, filenameadd=''):
    print 'input file directory:', pyxrfdir

    ''''
    E.g. fitsdata = 'det2' if fitted data is for ch2
    '''

    errorcodedef = [
    '1: Please provide a fileprefix as indicated in Xspress3 screen.;'+
    '2: Input directory is not a directory.;'+
    '3: Input directory does not exist.;'+
    '4: Input file does not exist.;'+
    '5: The file was not fitted.;'+
    '6: data size for ion chamber, positions or fitting data do not match.'
    '7: wrong input.']

    if fileprefix == None:
        if infile == None:
            print 'missing file keyword inputs.'
            print 'options 1 (priority): fileprefix = "2015_10_25_21_14"'
            print 'options 2 (when no fileprefix): infile = "2015_10_25_21_14_0.h5"'                        
            return 1, errorcodedef
        else:
            print "no file prefix provided, using keyword 'infile'"
            h5filein=infile
            print 'input file:', h5filein
    else:
        print 'ignore keyword "infile", using keyword "fileprefix"'
    
        if fileprefix[-1] == '_':
            fileprefix=fileprefix[0:-1]
        h5filein=fileprefix+'_pyxrf.h5'
        print 'input file:', fileprefix+'_pyxrf.h5'
        
    print 'ouput file directory:', foutdir

    #handle file exceptions:   
    ifindirdir, ifindirexist, ifinfileexist = checkfile(pyxrfdir, h5filein)
    print ifindirdir, ifindirexist, ifinfileexist
    if ifindirdir == False:
        print 'pyxrfdir='+pyxrfdir+'\nThis is not a directory.'
        return 2, errorcodedef

    elif ifindirexist == False:
        print 'pyxrfdir='+pyxrfdir+'\nThis directory does not exist.'
        return 3, errorcodedef

    elif ifinfileexist == False:
        print 'input file='+pyxrfdir+h5filein+'\nThis file does not exist.'
        return 4, errorcodedef
        
    else: 
        print 'Input directory and file exist.'

    if fitdata != 'detsum' and fitdata != 'det1' and fitdata != 'det2' and fitdata != 'det3' :
       print 'fitdata must = datasum, det1, det2, or det3'
       return 7, errorcodedef

    print 'Checking if the fitting was done'
    
    h5file = h5py.File(pyxrfdir+h5filein)
    fitnum='/xrfmap/'+fitdata+'/xrf_fit'
    fitname='/xrfmap/'+fitdata+'/xrf_fit_name'
    #fitdone = '/xrfmap/detsum/xrf_fit' in h5file
    fitdone = fitnum in h5file
    print h5filein
    if fitdone == False:
        print "This data file was not fitted."
        h5file.close
        return 5, errorcodedef
        
    else:
        print "This data file contains fitting results."
        
    print 'Converting Pyxrf data into Smak data format'

    #load text log file for energy and acqusition time
    dirf = string.split(h5filein, sep='_')
    print dirf
    textfiledir = '/nfs/xf05id1/data/'+ dirf[0] + '/' + dirf[1] + '/' + dirf[2] + '/' 
    if fileprefix == None:
        fileprefix = dirf[0] + '_' + dirf[1] + '_' + dirf[2] + '_'+ dirf[3] + '_' + dirf[4] 
    textfilename = 'log_' + fileprefix + '_srx-2dscan-sdd-timeout.py.txt'
    if notimeout == True:
        textfilename = 'log_' + fileprefix + '_srx-2dscan-sdd.py.txt'
    logfile=textfiledir+textfilename

    flog = open(logfile, 'r')
   
    line=flog.readline()
    line=line.replace(',', '=')
    line=line.replace(' ', '=')
    scriptline=string.split(line, sep = '=')
    k=0
    for i in scriptline:
        if i == '--acqtime':
            acqtime=scriptline[k+1]
            print 'acqusition time was:', acqtime
            break
        k=k+1       
    line=flog.readline()
    line=flog.readline()
    line=flog.readline()
    line=flog.readline()
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

    #read fitted h5 file with pyxrf format
    if filenameadd != '':
        filenameadd = '_'+filenameadd
    fout=foutdir+fileprefix+'_smak'+filenameadd+'.dat'   



    axisname = h5file['/xrfmap/positions/name']
    positions = h5file['/xrfmap/positions/pos']     
    #fitnum='/xrfmap/'+fitdata+'/xrf_fit'
    #fitname='/xrfmap/'+fitdata+'/xrf_fit_name'
    #xrf_fit = numpy.array(h5file['/xrfmap/detsum/xrf_fit'])     
    xrf_fit = numpy.array(h5file[fitnum])
    xrf_fit_name = numpy.array(h5file[fitname])    
    i0 = numpy.array(h5file['/xrfmap/scalers/val'])
    i0 = numpy.squeeze(i0)
    i0 = i0*i0f        
    
    print xrf_fit.dtype
    print xrf_fit.shape
    (numfitelement, ysize, xsize) =  xrf_fit.shape
    print xrf_fit_name
  

    #check if array size matches
    #print 'ysize, xsize, ypos, xpos:', ysize, xsize, ypos, xpos 
    sizematchflag=True  
    posxdim, posydim = positions.shape[2], positions.shape[1]
    i0xdim, i0ydim = i0.shape[1], i0.shape[0]
    fitxdim, fitydim = xrf_fit.shape[2], xrf_fit.shape[1]

    if (posxdim != i0xdim) or (i0xdim != fitxdim) or  (fitxdim !=posxdim):          
        print 'data size for ion chamber, positions or fitting data do not match in X.'
        sizematchflag = False
    if (posydim != i0ydim) or (i0ydim != fitydim) or  (fitydim !=posydim):          
        print 'data size for ion chamber, positions or fitting data do not match in Y.'
        sizematchflag = False  
    
    if sizematchflag == False:
        print 'positions.shape, i0.shape, xrf_fit.shape:', positions.shape, i0.shape, xrf_fit.shape
        return 6, errorcodedef 
    
    #write data file
    ##write headers:
    f = open(fout, 'w') 

    f.write('* Abscissa points :   '+str(len(positions[0,0,:]))+'\n')
    f.write('* Ordinate points :   '+str(len(positions[1,:,0]))+'\n')
    f.write('* BLANK LINE\n')
    f.write('* Data Channels :   '+str(len(xrf_fit_name)+1)+'\n')
    f.write('* Data Labels : ch2_I0\t')
    for mapname in xrf_fit_name:        
        f.write(mapname+'\t')
    f.write('\n')    
    f.write('* Comments: '+comments+'\n') 
    f.write('* dwell time = '+str(acqtime)+'\n') 
    f.write('*\n')    
    f.write('*\n')  
    f.write('* BLANK LINE\n')
    f.write('* Abscissa points requested :\n')
    f.write('* ')
    for pos in positions[0,0,:]:        
        f.write(str(pos)+'\t')            
    f.write('\n') 
    f.write('* BLANK LINE\n')
    f.write('* BLANK LINE\n')                
    f.write('* Ordinate points requested :\n')
    f.write('* ')
    for pos in positions[1,:,0]:        
        f.write(str(pos)+'\t')            
    f.write('\n')    
    f.write('* BLANK LINE\n')
    f.write('* BLANK LINE\n')
    f.write('* Energy points requested:\n')
    f.write('* '+str(energy)+'\n')
    f.write('* BLANK LINE\n')
    f.write('* DATA\n')
       

    for ypos in xrange(0,ysize):
        for xpos in xrange(0,xsize):
            
          
            f.write(str(positions[1,ypos, xpos])+'\t'+str(positions[0,ypos,xpos])+'\t'+str(i0[ypos,xpos])+'\t')
            mapnum = 0
            for mapname in xrf_fit_name:        
                f.write(str(xrf_fit[mapnum,ypos, xpos])+'\t')
                mapnum = mapnum+1
            f.write('\n')
    

    print 'Done saving! '+fout
    print '\n'
    f.close()
    flog.close()
    h5file.close
    return 0, errorcodedef