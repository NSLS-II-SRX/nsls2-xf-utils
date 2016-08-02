import h5py
import matplotlib.pyplot as plt
import numpy
import srxdatadir
import SRXenergy

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

def sumallptallch(x3dir=srxdatadir.dfx3filedir, fileprefix=None, roil=0, roih=4095, filenum=0):
   
    x=range(0,4096)
    x3file = h5py.File(x3dir+fileprefix+'_'+str(filenum)+'.hdf5', 'r')      
    mcadata = x3file['/entry/instrument/detector/data']
        
    fileshape=mcadata.shape
    print(fileshape)
    
    #ch1mcapt = numpy.sum(numpy.array(mcadata[:,:,0,:]), axis=0)
    #ch2mcapt = numpy.sum(numpy.array(mcadata[:,:,1,:]), axis=0)
    #ch3mcapt = numpy.sum(numpy.array(mcadata[:,:,2,:]), axis=0)
    
    sumptmca = numpy.sum(numpy.array(mcadata), axis=0)  #sum all different points, 0 axis
    sumallchmca = numpy.sum(numpy.array(sumptmca), axis=1) #sum three different elements,  1 axis
    sumallchmca=numpy.squeeze(sumallchmca)    
                          
    print(str(len(x[roil:roih]))+str(len(sumallchmca[roil:roih])))
                          
    p=plt.plot(x[roil:roih],sumallchmca[roil:roih])
    plt.xlabel('channel number')    

    plt.ylabel('fluorescence signal - sum of 3 channels roi (a.u.)')
    plt.show(p)
    
def xrfxanescheck(x3dir=srxdatadir.dfx3filedir, fileprefix=None, roil=0, roih=4095, filenum=0, ptlist=[0, -1]):
   
    x=range(0,4096)
    x3file = h5py.File(x3dir+fileprefix+'_'+str(filenum)+'.hdf5', 'r')      
    mcadata = x3file['/entry/instrument/detector/data']
    bragg = x3file['/entry/instrument/NDAttributes/BraggAngle']
        
    fileshape=mcadata.shape
    print(fileshape)
    
    #ch1mcapt = numpy.sum(numpy.array(mcadata[:,:,0,:]), axis=0)
    #ch2mcapt = numpy.sum(numpy.array(mcadata[:,:,1,:]), axis=0)
    #ch3mcapt = numpy.sum(numpy.array(mcadata[:,:,2,:]), axis=0)
    
    allchmca = numpy.sum(numpy.array(mcadata), axis=2) #sum three different elements,  1 axis   
    
    for pt in ptlist:       
        ptallchmca=allchmca[pt,:,:]   
        ptallchmca=numpy.squeeze(ptallchmca)                                                  
        p=plt.plot(x[roil:roih],ptallchmca[roil:roih], label=str(SRXenergy.BraggtoE(bragg[pt])))
 
    plt.xlabel('channel number')    

    plt.ylabel('fluorescence signal - sum of 3 channels roi (a.u.)')
    plt.legend(loc=1)
    plt.show(p)

def xanesstackcheck(x3dir=srxdatadir.dfx3filedir, fileprefixList=None, roil=0, roih=4095, filenum=0, 
                    datach = 'ch1'):
   
    for fileprefix in fileprefixList:   
        x=range(0,4096)
        x3file = h5py.File(x3dir+fileprefix+'_'+str(filenum)+'.hdf5', 'r')      
        mcadata = x3file['/entry/instrument/detector/data']
        mcadata=numpy.squeeze(mcadata)
        
        fileshape=mcadata.shape
        print(fileshape)
    
        if datach == 'ch1':
            readdata = numpy.array(mcadata[:,:,0,:])
        elif datach == 'ch2':
            readdata = numpy.array(mcadata[:,:,1,:])
        elif datach == 'ch3':
            readdata = numpy.array(mcadata[:,:,2,:])
        elif datach == 'chsum':
            readdata = numpy.array(mcadata[:,:,0,:])
            readdata = readdata + numpy.array(mcadata[:,:,1,:])
            readdata = readdata + numpy.array(mcadata[:,:,2,:])
    
        sumptmca = numpy.sum(numpy.array(readdata), axis=0)  #sum all different points, 0 axis
        sumptmca = numpy.sum(numpy.array(sumptmca), axis=0)  #sum all different points, 1 axis
                          
        print(str(len(x[roil:roih]))+str(len(sumptmca[roil:roih])))                                           
        p=plt.plot(x[roil:roih],sumptmca[roil:roih])
    plt.xlabel('channel number')    
    plt.ylabel('fluorescence signal (a.u.)')
    plt.show(p)
