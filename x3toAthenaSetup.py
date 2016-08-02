import h5py
import matplotlib.pyplot as plt
import numpy
#import srxmcaEnergyCal
import SRXenergy
import string
import srxdatadir
import sys

# Read the HDF5 file
#file = h5py.File('/Users/admin/Documents/proj_4.hdf')

##################################

#indir = '/data/XSPRESS3/2015-3/in-house/'
#infile = '2015_10_24_20_58' #'Pb-Sn yellow standard 1eV
#eline=1060 #Au
#intext='Pb-Sn yellow standard'
#numframe=1
#filenum=0

#ploti0 = False
#normalizationbyPtic = True
#scaling = False
#scalingpt=5

#handle single frame for now

def x3toAthena(x3dir=srxdatadir.dfx3filedir, fileprefix=None, roil=None, roih=None, eline = None, roilr=-10, roihr=+10, athenadir=srxdatadir.dfathenaoutdir, sampleinfo = 'SRX sample', 
               numframe=1, filenum = 0, smooth = False, smoothnum=None, ch = None, notimeout = False, i0f=1.0e8, filepost='',
               plot=False, normalization = False, scaling = False, scalingpt = 5, savetoAthena=True,  #for plot = Ture only options
               xbragg = False, returnarray = False 
               ):

    '''
    [Example] give roil and roih directly
    SRXfileio.x3toAthena(fileprefix='2015_11_4_21_51', roil=834, roih=1424, sampleinfo='MET PbSnYellow')

    [Example] give center and define a window
    SRXfileio.x3toAthena(fileprefix='2015_11_4_19_34', eline=830, roilr=-10, roihr=10, sampleinfo='HfAl3, hydrated, point1')

    '''

    if roil==None:
        if eline != None:
            roil=eline+roilr
        else:
            print('missing roil (roi lowest channel)')
    if roih==None:
        if eline != None:
            roih=eline+roihr
        else:
            print('missing roil (roi highest channel)')        
    
    print('input file directory: '+x3dir)

    if fileprefix == None:
        print("please provide a fileprefix as indicated in Xspress3 screen. E.g. '2015_10_25_21_14'")
        sys.exit()
    if fileprefix[-1] == '_':
        fileprefix=fileprefix[0:-1]
        
    print('input file: '+ fileprefix+'_'+str(filenum))

    if savetoAthena==True:

        print('ouput file directory: '+ athenadir)
        print('output file: '+ fileprefix+'_'+str(filenum)+'_Athena.txt')

        if i0f != 1.0:
            filepost=filepost+'i0f'
    
        faout=open(athenadir+fileprefix+'_'+str(filenum)+'_'+str(filepost)+'_Athena.txt','w')
    
        faout.write('X3HDF5toAthena Datafile V1\n')   
        faout.write('Raw data: '+fileprefix+str(filenum)+'.hdf5 created on SRX beamline, NSLSII\n') 
        faout.write('HDCM crystal = Si 111. \n')       
        faout.write('Sample:'+sampleinfo+'\n')
        faout.write('Energy ROI selection (channels): '+str(roil) + '-' + str(roih)+ '; Total range: ' + str((roih-roil)*10) + ' eV; i0factor:' + str(i0f) + '\n')
        if smooth==True:
            faout.write('Smooth was applied on the data with averaging number of points: '+str(smoothnum)+'\n')
    
        faout.write('-----------------------------------------------------------------------------\n')
        
        faout.write('Energy\t\tIf\t\tI0\n')


    #load i0 and energy from text file
    #dirf = string.split(fileprefix, sep='_')
    dirf = fileprefix.split(sep='_')
    textfiledir = '/nfs/xf05id1/data/'+ dirf[0] + '/' + dirf[1] + '/' + dirf[2] + '/' 
    textfilename = 'log_' + fileprefix + '_srx-coord-energy-sdd-timeout.py.txt'
    if notimeout == True:
        textfilename = 'log_' + fileprefix + '_srx-coord-energy-sdd.py.txt'
    #print textfilename
    textfile=textfiledir+textfilename
    print('reading i0 and energy from: '+ textfile)
    
    offset=8.5e-10 #for i0

    i0=[]
    energyAxis=[]
    flag = False 
    with open(textfile, 'r') as f:
        while True:
            line=f.readline()
            if not line: break
            if line[0] != '#':
                #print line
#                a=string.split(line)
                a=line.split()
                #print a
                i0pt = float(a[13])
                if xbragg == False: 
                    ept=float(a[3])
                    fct = 1000.
                else:
                    ept=float(a[0])
                    fct = 1.
                
                #print i0pt
                if i0pt == 0:  #handle when f460 gives out zero
                    flag = True
                else:
                    if flag == True:
                        i0.append(i0pt)
                        flag = False                    
                    i0.append(i0pt)   #ion chamber reading
                    energyAxis.append(ept/fct)

    i0array = numpy.array(i0)
    i0array=numpy.abs(i0array-offset)*i0f

    numenergypt=len(energyAxis)

    #load x3 hdf5 data        
    x3file = h5py.File(x3dir+fileprefix+'_'+str(filenum)+'.hdf5', 'r')      
    mcadata = x3file['/entry/instrument/detector/data']
        
    #print mcadata.shape
        
    ch1roi=numpy.zeros(numenergypt)
    ch2roi=numpy.zeros(numenergypt)
    ch3roi=numpy.zeros(numenergypt)
    
    energy = range(numenergypt)
    #print 'numframe:', numframe
    for energypt in energy:
        for framenum in range(numframe):
            ch1mca = mcadata[energypt,framenum,0,:].flat
            ch2mca = mcadata[energypt,framenum,1,:].flat
            ch3mca = mcadata[energypt,framenum,2,:].flat
    
            ch1roi[energypt]=ch1roi[energypt]+numpy.sum(ch1mca[roil:roih])
            ch2roi[energypt]=ch2roi[energypt]+numpy.sum(ch2mca[roil:roih])
            ch3roi[energypt]=ch3roi[energypt]+numpy.sum(ch3mca[roil:roih])
   
    if ch == 1:
        roisum = ch1roi
    elif ch == 2:
        roisum = ch2roi
    elif ch == 3:
        roisum = ch3roi
    else:
        roisum = ch1roi+ch2roi+ch3roi
        
    print('number of energy points: '+str(len(energyAxis)))
    #print len(roisum)
    
    pre1=pre2=pre3=str()

    plotarray = roisum
    if smooth == True:
        plotarray_sumsm=list(plotarray)    
        if smoothnum == 5:
            pre3 = 'smooth5'
            for i in xrange(len(plotarray)):
            #    print i
                if (i != 0) and (i != (len(plotarray)-1)):
                    if ((i == 1) or (i == (len(plotarray)-2))):
                        plotarray_sumsm[i]= (plotarray[i-1]+plotarray[i+1])/2 
                    else:
                        plotarray_sumsm[i]= (plotarray[i-2]+plotarray[i-1]+plotarray[i]+plotarray[i+1]+plotarray[i+2])/5 
        if smoothnum == 3:
            pre3 = 'smooth3'            
            for i in xrange(len(plotarray)):
            #    print i
                if (i != 0) and (i != (len(plotarray)-1)):
                    plotarray_sumsm[i]= (plotarray[i-1]+plotarray[i+1])/2 
        else:
            print('only smoothnum = 3 or 5 are supported now')
            
        
        plotarray=roisum=plotarray_sumsm


    if savetoAthena==True:
        for i in range(numenergypt):
            estring = str(energyAxis[i])
            #tmp = string.split(estring, sep = '.')
            #if len(tmp[1])==1:
            #    estring=estring+'0'
            line=estring+'\t'+str(roisum[i])+'\t'+str(i0array[i])+'\n'
            faout.write(line)

#####for plot=Ture optino only:#################

    if normalization == True:
        plotarray = roisum/i0array
        pre2='normalized '

    if scaling == True:
        zero=numpy.average(plotarray[0:scalingpt])
        one=numpy.average(plotarray[-1:-1*(scalingpt+1):-1])
        plotarray=(plotarray-zero)/(one-zero)
        pre1='scaled '

    if plot == True:
        p=plt.plot(energyAxis,plotarray, label=str(fileprefix)+':'+sampleinfo) 
        if xbragg == False:        
            plt.xlabel('energy (keV)')
        else: 
            plt.xlabel('bragg (deg)')

        plt.ylabel(pre1+pre2+pre3+'fluorescence signal - sum of 3 channels roi (a.u.)')
        plt.legend(loc=4)
        plt.show(p)

 
    x3file.close()
    if savetoAthena==True:
        faout.close()

    if returnarray == True:    
        return energyAxis, plotarray 
