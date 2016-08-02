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

def TdiodetoAthena(fileprefix=None, athenadir=srxdatadir.dfathenaoutdir, sampleinfo = 'SRX sample', 
               smooth = False, smoothnum=None, ch = None,  i0f=1.0e8, filepost='',
               plot=False, normalization = False, scaling = False, scalingpt = 5, savetoAthena=True,  #for plot = Ture only options
               xbragg = False, returnarray = False 
               ):

    '''
    [Example] give roil and roih directly
    SRXfileio.x3toAthena(fileprefix='2015_11_4_21_51', roil=834, roih=1424, sampleinfo='MET PbSnYellow')

    [Example] give center and define a window
    SRXfileio.x3toAthena(fileprefix='2015_11_4_19_34', eline=830, roilr=-10, roihr=10, sampleinfo='HfAl3, hydrated, point1')

    '''

    if fileprefix == None:
        print "please provide a fileprefix as indicated in Xspress3 screen. E.g. '2015_10_25_21_14'"
        sys.exit()
    if fileprefix[-1] == '_':
        fileprefix=fileprefix[0:-1]
        
    print 'input file:', fileprefix

    if savetoAthena==True:

        print 'ouput file directory:', athenadir
        print 'output file:', fileprefix+'_'+'_Athena.txt'

        if i0f != 1.0:
            filepost=filepost+'i0f'
    
        faout=open(athenadir+fileprefix+'_'+'_'+str(filepost)+'_Athena.txt','w')
    
        faout.write('X3HDF5toAthena Datafile V1\n')   
        faout.write('Raw data: '+fileprefix + 'created on SRX beamline, NSLSII\n') 
        faout.write('HDCM crystal = Si 111. \n')       
        faout.write('Sample:'+sampleinfo+'\n')
        if smooth==True:
            faout.write('Smooth was applied on the data with averaging number of points: '+str(smoothnum)+'\n')
    
        faout.write('-----------------------------------------------------------------------------\n')
        
        faout.write('Energy\t\tIt\t\tI0\n')


    #load i0 and energy from text file
    dirf = string.split(fileprefix, sep='_')
    textfiledir = '/nfs/xf05id1/data/'+ dirf[0] + '/' + dirf[1] + '/' + dirf[2] + '/' 
    textfilename = 'log_' + fileprefix + '_srx-coord-energy-timeout-e.py.txt'
    #print textfilename
    textfile=textfiledir+textfilename
    print 'reading i0 and energy from:', textfile
    
    offset=8.2e-10 #for i0

    i0=[]
    it=[]
    energyAxis=[]
    flag = False 
    with open(textfile, 'r') as f:
        #line=f.readline()
        #line=f.readline()
        #line=f.readline()
        while True:
            line=f.readline()
            if not line: break
            if line[0] != '#':
                #print line
                a=string.split(line)
                #print a
                itpt = float(a[9])
                i0pt = float(a[10])
                if xbragg == False: 
                    ept=float(a[1])
                    fct = 1.
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
                    it.append(itpt)
                    energyAxis.append(ept/fct)

    i0array = numpy.array(i0)
    i0array=numpy.abs(i0array-offset)*i0f
    itarray = numpy.array(it)

    numenergypt=len(energyAxis)


    if savetoAthena==True:
        for i in range(numenergypt):
            estring = str(energyAxis[i])
            #tmp = string.split(estring, sep = '.')
            #if len(tmp[1])==1:
            #    estring=estring+'0'
            line=estring+'\t'+str(itarray[i])+'\t'+str(i0array[i])+'\n'
            faout.write(line)

#####for plot=Ture optino only:#################

    if normalization == True:
        plotarray = itarray/i0array
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

        plt.ylabel(pre1+pre2+'transmission diode (arb. u)')
        plt.legend(loc=4)
        plt.show(p)

    if savetoAthena==True:
        faout.close()

    if returnarray == True:    
        return energyAxis, plotarray 
