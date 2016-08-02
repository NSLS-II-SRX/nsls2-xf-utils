import h5py
import matplotlib.pyplot as plt
import numpy
#import srxmcaEnergyCal
import SRXenergy
import string

# Read the HDF5 file
#file = h5py.File('/Users/admin/Documents/proj_4.hdf')

##################################
filenum=0

###########

filedir = '/data/XSPRESS3/2015-3/in-house/'
file1 = '2015_10_24_20_12_' #'Pb-Sn yellow standard test
file2 = '2015_10_24_20_32_' #'Pb-Sn yellow standard 1eV
file3 = '2015_10_24_20_58_' #'Pb-Sn yellow standard 1eV
file4 = '2015_10_24_21_40_' #'Pb-Sn yellow standard 1eV
file5 = '2015_10_24_22_19_' #'Pb-Sn yellow standard erange
file6 = '2015_10_24_22_37_' #'Pb-Sn yellow standard erange
file7 = '2015_10_24_22_48_' #'Pb-Sn yellow standard erange, ugap enabled
file8 = '2015_10_26_15_44_' #'Pb-Sn yellow standard genE, ugap disabled; noc2x correction
file9 = '2015_10_26_15_50_' #'Pb-Sn yellow standard genE, ugap disabled; noc2x correction
file10 = '2015_10_26_16_9_' #'Pb-Sn yellow standard genE, ugap disabled; noc2x correction
file11 = '2015_10_26_16_47_' #'Pb-Sn yellow standard genE, ugap disabled; noc2x correction
file12 = '2015_10_26_17_0_' #'Pb-Sn yellow standard genE, ugap disabled; withc2x correction
file13 = '2015_10_26_17_11_' #'Pb-Sn yellow standard genE, ugap disabled; noc2x correction
file14 = '2015_10_26_18_37_' #'Pb-Sn yellow standard genE, ugap disabled; withc2x correction, 3s wait
file15 = '2015_10_26_19_11_' #'Pb-Sn yellow standard genE, ugap disabled; noc2x correction, 3s wait
file16 = '2015_10_26_19_32_' #'Pb-Sn yellow standard genE, ugap disabled; noc2x correction, 1s wait, KBs killed
file17 = '2015_10_26_19_55_' #'Pb standard genE, ugap disabled; noc2x correction, 1s wait, KBs killed

econfigFile1='/nfs/xf05id1/energyScanConfig/20151024_Pbtest1.text'
econfigFile2='/nfs/xf05id1/energyScanConfig/20151024_Pb_01.text'
econfigFile3='/nfs/xf05id1/energyScanConfig/20151024_Pb_02.text'

econfigFile4='/nfs/xf05id1/energyScanConfig/20151026_Pb_test02.text'
econfigFile5='/nfs/xf05id1/energyScanConfig/20151026_Pb_test03.text'
econfigFile6='/nfs/xf05id1/energyScanConfig/20151026_Pb_test04.text'

econfigFile7='/nfs/xf05id1/energyScanConfig/20151026_Pb_test06.text'  #correct c2x, ugap disabled, genErange
econfigFile8='/nfs/xf05id1/energyScanConfig/20151026_Pb_test07_noc2x.text'  #no correct c2x, ugap disabled, genErange

fileprefixList=[file1, file2, file3, file4, file5]
econfigFileList = [econfigFile1,econfigFile2,econfigFile2,econfigFile2,econfigFile3]
numframeList=[1,1,1,1,1,1,1,1,1,1]
sample=['Pb-Sn yellow standard','Pb-Sn yellow standard','Pb-Sn yellow standard','Pb-Sn yellow standard','Pb-Sn yellow standard']


fileprefixList=[file5, file6, file7]
econfigFileList = [econfigFile3, econfigFile3, econfigFile3]
numframeList=[1,1,1,1,1,1,1,1,1,1]
sample=['Pb-Sn y', 'Pb-Sn y', 'Pb-Sn y']

fileprefixList=[file8, file9, file10, file11,file12]#, file13]
econfigFileList = [econfigFile4, econfigFile5, econfigFile5,econfigFile6,econfigFile7,econfigFile8]
numframeList=[1,1,1,1,1,1,1,1,1,1]
sample=['Pb-Sn y', 'Pb-Sn y', 'Pb-Sn y', 'Pb-Sn y', 'Pb-Sn y', 'Pb-Sn y']

fileprefixList=[file12, file13, file14, file15, file16]#, file17]
econfigFileList = [econfigFile7,econfigFile8,econfigFile7,econfigFile8,econfigFile8,econfigFile8]
numframeList=[1,1,1,1,1,1,1,1,1,1]
sample=['withc2x 1s', 'noc2x 1s', 'withc2x 3s', 'noc2x 3s','noc2x 1s M2Y_killed', 'Pb standard noc2x 1s M2Y_killed', 'Pb-Sn y']


#normalization = False
ploti0 = True
normalizationbyPtic = False
scaling = False
scalingpt=5
textfiledir = '/nfs/xf05id1/data/2015/10/26/'


roil=1000
roih=1150
#
######## rotated, reflective
#fileprefixList = ['19_25_','19_30_', '19_45_'] #[45deg, 45degwithy+5um, 30deg]
#element='Ni'
#econfigFileList = [econfigFileNi1,econfigFileNi1,econfigFileNi1,econfigFileNi1,econfigFileNi1,econfigFileNi1,econfigFileNi1]
#numframeList=[1,1,1,1,1,1,1]
#roil=735
#roih=755



######load Energy Axis###############
#numenergypt=0
#with open(econfigFile, 'r') as feconf:
#    while True:
#        line=feconf.readline()
#        if not line: break
#        numenergypt=numenergypt+1
#        lineList=line.split(" ")
#        bragg=float(lineList[0])
#        energyAxis.append(SRXenergy.BraggtoE(bragg, show=False))
#        print energyAxis                
#        

filect=0
n=4
fig=plt.figure(1, figsize=(3*n,2*n))
for fileprefix in fileprefixList:
    
    #load i0
    textfilename = 'log_' + fileprefix + 'srx-coord-energy-sdd.py.txt'
    print textfilename
    textfile=textfiledir+textfilename
    
    i0=[]
    flag = False 
    with open(textfile, 'r') as f:
        while True:
            line=f.readline()
            if not line: break
            if line[0] != '#':
                #print line
                a=string.split(line)
                #print a
                i0pt = float(a[13])            
                #print i0pt
                if i0pt == 0:
                    flag = True
                else:
                    if flag == True:
                        i0.append(i0pt)
                        flag = False                    
                    i0.append(i0pt)   #ion chamber reading
        
        
    
    i0array = numpy.array(i0)
    #i0array=i0array*(-1.0)    
    offset=8.5e-10
    i0array=numpy.abs(i0array-offset)
    
    econfigFile=econfigFileList[filect]
    filect=filect+1
    
    #####load Energy Axis###############
    energyAxis=[]
    numenergypt=0
    with open(econfigFile, 'r') as feconf:
        while True:
            line=feconf.readline()
            if not line: break
            numenergypt=numenergypt+1
            lineList=line.split(" ")
            bragg=float(lineList[0])
            energyAxis.append(SRXenergy.BraggtoE(bragg, show=False))
            #print energyAxis                

    ch1sum= numpy.zeros((4096))
    ch2sum= numpy.zeros((4096))
    ch3sum= numpy.zeros((4096))
    
    #xenergy = srxmcaEnergyCal.srxmcaenergy()
    
    print filedir+fileprefix+str(filenum)+'.hdf5'
    infile = h5py.File(filedir+fileprefix+str(filenum)+'.hdf5', 'r')
    name = filedir+fileprefix+str(filenum)+'.hdf5'
    print name
    print len(infile)
        
    x=range(0,4096)
    mcadata = infile['/entry/instrument/detector/data']
        
    print mcadata.shape
        
    ch1roi=numpy.zeros(numenergypt)
    ch2roi=numpy.zeros(numenergypt)
    ch3roi=numpy.zeros(numenergypt)

    i0ch1roi=numpy.zeros(numenergypt)
    i0ch2roi=numpy.zeros(numenergypt)
    i0ch3roi=numpy.zeros(numenergypt)
    
    energy = range(numenergypt)
    numframe=numframeList[filect-1]
    print 'numframe:', numframe
    for energypt in energy:
        for framenum in range(numframe):
            ch1mca = mcadata[energypt,framenum,0,:].flat
            ch2mca = mcadata[energypt,framenum,1,:].flat
            ch3mca = mcadata[energypt,framenum,2,:].flat
    
            ch1roi[energypt]=ch1roi[energypt]+numpy.sum(ch1mca[roil:roih])
            ch2roi[energypt]=ch2roi[energypt]+numpy.sum(ch2mca[roil:roih])
            ch3roi[energypt]=ch3roi[energypt]+numpy.sum(ch3mca[roil:roih])

#            i0ch1roi[energypt]=ch1roi[energypt]+numpy.sum(ch1mca[i0roil:i0roih])
#            i0ch2roi[energypt]=ch2roi[energypt]+numpy.sum(ch2mca[i0roil:i0roih])
#            i0ch3roi[energypt]=ch3roi[energypt]+numpy.sum(ch3mca[i0roil:i0roih])

    
    roisum = ch1roi+ch2roi+ch3roi
 #   i0sum = i0ch1roi+i0ch2roi+i0ch3roi
        
    print len(energyAxis) 
    print len(roisum)
    
#    if normalization == True:
#        p=plt.plot(energyAxis,roisum/i0sum)
#
#    elif ploti0 == True:
#        p=plt.plot(energyAxis,i0sum)
#    else:
#            p=plt.plot(energyAxis,roisum)  

    pre1=str()
    pre2=str()

    if normalizationbyPtic == True:
        plotarray = roisum/i0array
        pre2='normalized '
    elif ploti0 == True:
        plotarray = i0array
    else:
        plotarray = roisum      
        
    if scaling == True:
        zero=numpy.average(plotarray[0:scalingpt])
        one=numpy.average(plotarray[-1:-1*(scalingpt+1):-1])
        print zero
        print one
        plotarray=(plotarray-zero)/(one-zero)
        print plotarray
        pre1='scaled '

    p=plt.plot(energyAxis,plotarray, label=str(fileprefix)+':'+sample[filect-1]) 
    infile.close()
    feconf.close()
    
plt.xlabel('energy (keV)')


plt.ylabel(pre1+pre2+'fluorescence signal - sum of 3 channels roi (a.u.)')
plt.legend(loc=4)
plt.show(p)
