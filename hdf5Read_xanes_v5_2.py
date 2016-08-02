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

filedir = '/nfs/xf05id1/data/hdf5/20150806/'

file1='2015_8_6_15_27_' #Fe coarse
file2='2015_8_6_15_37_' #Fe fine
file3='2015_8_6_16_47_' #pig coarse, on pt1 '2015_8_6_16_23_', (-6, -36)
file4='2015_8_6_16_53_' #pig fine, on pt1
file5='2015_8_6_17_31_'#pig fine, on pt1
file6='2015_8_6_18_10_' #pig coarse, on pt2 '2015_8_6_16_23_', (32, -35)
file7='2015_8_6_18_23_' #pig coarse, on pt3 '2015_8_6_16_23_', (-9, -62)

file8='2015_8_6_18_58_' #pig coarse, on pt4 '2015_8_6_18_36_', (-13, -5)
file9='2015_8_6_19_5_' #pig fine, on pt4 '2015_8_6_18_36_', (-13, -5)
file10='2015_8_6_19_22_' #pig fine, on pt5 '2015_8_6_18_36_', (-8, -35)
file11='2015_8_6_19_43_' #Fe fine, larger energy range

econfigFile='/nfs/xf05id1/energyScanConfig/20150806_Fe_no1.text'
econfigFile2='/nfs/xf05id1/energyScanConfig/20150806_Fe_no2.text'
econfigFile3='/nfs/xf05id1/energyScanConfig/20150806_Fe_no3.text'
econfigFile4='/nfs/xf05id1/energyScanConfig/20150806_Fe_no4.text'


#Juergen's NASA sample
#fileprefixList = [file1,file2 , file3, file4, file5, file6]  
#econfigFileList = [econfigFile, econfigFile2,econfigFile3,econfigFile4,econfigFile4,econfigFile3]
#numframeList=[1,1,1,1,1,1]
#sample=['Fefoilcoarse', 'Fefoilfine', 'pigeonite(-6,-36)coarse','pigeonite(-6,-36)fine1','pigeonite(-6,-36)fine2','pigeonite(32,-35)coarse']

#fileprefixList = [file2 , file3, file4, file5, file6, file7]  
#econfigFileList = [econfigFile2,econfigFile3,econfigFile4,econfigFile4,econfigFile3,econfigFile3]
#numframeList=[1,1,1,1,1,1]
#sample=['Fefoilfine', 'pigeonite(-6,-36)coarse','pigeonite(-6,-36)fine1','pigeonite(-6,-36)fine2','pigeonite(32,-35)coarse','pigeonite(-9,-62)coarse']

#fileprefixList = [file2 , file3, file4, file5, file6, file7, file8]  
#econfigFileList = [econfigFile2,econfigFile3,econfigFile4,econfigFile4,econfigFile3,econfigFile3,econfigFile3]
#numframeList=[1,1,1,1,1,1,1]
#sample=['Fefoilfine', 'pigeonite(-6,-36)coarse','pigeonite(-6,-36)fine1','pigeonite(-6,-36)fine2','pigeonite(32,-35)coarse','pigeonite(-9,-62)coarse', 'region3-pigeonite(-13,-5)coarse']

fileprefixList = [file5, file9, file10, file11]  
econfigFileList = [econfigFile4,econfigFile4,econfigFile4,econfigFile4]
numframeList=[1,1,1,1,1,1,1]
sample=['region2-pigeonite(-6,-36)fine2','region3-pigeonite(-13,-5)fine','region3-pigeonite(-8,-35)fine', 'Fe foil fine2']

roil=640-10
roih=640+10

####test with Shen
#filedir = '/nfs/xf05id1/data/hdf5/20150807/'
#file1 = '2015_8_7_15_24_' #Ni rough scan
#file1 = '2015_8_7_15_35_' #Ni rough scan
#file1 = '2015_8_7_15_56_' #Ni rough scan
#file1 = '2015_8_7_16_12_' #Ni rough scan, transmission geometry
#file1 = '2015_8_7_16_18_' #Ni rough scan, transmission geometry
#
#econfigFile1='/nfs/xf05id1/energyScanConfig/20150807_Nino3.text'
#sample=['transmissionNi']
#
#roil=747-10
#roih=747+10
#
##file1 = '2015_8_7_16_29_' #Pt rough scan, transmission geometry
#file1 = '2015_8_7_16_40_' #Pt rough scan, transmission geometry
##econfigFile1='/nfs/xf05id1/energyScanConfig/20150807_Ptno1.text'
#econfigFile1='/nfs/xf05id1/energyScanConfig/20150807_Ptno2.text'
#
#sample=['transmissionPt']
#roil=940-10
#roih=940+10
#
#fileprefixList = [file1]  
#econfigFileList = [econfigFile1]
#numframeList=[1,1,1,1,1,1,1]
##sample=['transmissionNi']
#
#
filedir = '/nfs/xf05id1/data/hdf5/2015_8_7/'

file1 = '2015_8_7_20_52_' #Pb, Met1, location2, npoint (-10, -15)
file2 = '2015_8_7_21_11_' #Pb, Met3, location2, npoint (-40, -35)
file3 = '2015_8_7_21_28_' #Pb-Sn yellow standard, rough scan
file4 = '2015_8_7_21_38_' #Pb-Sn yellow standard, fine scan
file5 = '2015_8_7_22_9_' #Pb palmitate standard, fine scan
file6 = '2015_8_7_22_27_' #Pb palmitate standard, fine scan
file7 = '2015_8_7_22_57_' #Pb-Sn yellow standard, fine scan v
file8 = '2015_8_7_23_21_' #Pb2O3 standard, fine scan
file9 = '2015_8_7_23_49_' #Pb palmitate standard, fine scan, change sample angle

#filedir = '/nfs/xf05id1/data/hdf5/2015_8_8/'
file10 = '2015_8_8_0_18_' #Pb azelate standard, fine scan, change sample angle

econfigFile1='/nfs/xf05id1/energyScanConfig/20150807_Pb_no1.text'
econfigFile2='/nfs/xf05id1/energyScanConfig/20150807_Pb_no2.text'

sample=['Met1Pb','Met3Pb', 'Pb-Sn yellow standard','Pb-Sn yellow standard','Pb palmitate','Pb palmitate','Pb-Sn yellow standard', 'Pb2O3 standrad', 'Pb palmitate']

roil=1050-10
roih=1050+10
fileprefixList = [file1, file2, file3, file4, file5, file6, file7, file8, file9]  
econfigFileList = [econfigFile1,econfigFile1,econfigFile1,econfigFile2,econfigFile2,econfigFile2,econfigFile2,econfigFile2,econfigFile2, econfigFile2]
numframeList=[1,1,1,1,1,1,1,1,1,1,1,1]
#
fileprefixList = [file7, file8, file9]  
econfigFileList = [econfigFile2,econfigFile2,econfigFile2]
numframeList=[1,1,1,1,1,1,1,1,1,1]
sample=['Pb-Sn yellow standard', 'Pb2O3 standrad', 'Pb palmitate']

#fileprefixList = [file10]  
#econfigFileList = [econfigFile2,econfigFile2,econfigFile2]
#numframeList=[1,1,1,1,1,1,1,1,1,1]
#sample=['Pb azelate']

i0roil=288
i0roih=302

#normalization = False
ploti0 = False
normalizationbyPtic = False
scaling = False
scalingpt=5
textfiledir = '/nfs/xf05id1/data/2015/8/6/'
textfiledir = '/nfs/xf05id1/data/2015/8/7/'
#textfiledir = '/nfs/xf05id1/data/2015/8/8/'

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
    textfilename = 'log_' + fileprefix[5::] + 'srx-coord-energy-sdd.py.txt'
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
    
#    xenergy = srxmcaEnergyCal.srxmcaenergy()
    
    infile = h5py.File(filedir+fileprefix+str(filenum)+'.hdf5')
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

            i0ch1roi[energypt]=ch1roi[energypt]+numpy.sum(ch1mca[i0roil:i0roih])
            i0ch2roi[energypt]=ch2roi[energypt]+numpy.sum(ch2mca[i0roil:i0roih])
            i0ch3roi[energypt]=ch3roi[energypt]+numpy.sum(ch3mca[i0roil:i0roih])

    
    roisum = ch1roi+ch2roi+ch3roi
    i0sum = i0ch1roi+i0ch2roi+i0ch3roi
        
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
