import numpy
import string
from matplotlib import pyplot
import subprocess 
import scipy as sp
import scipy.optimize
import x3toAthenaSetup as xa
#plan:
#1. load 4 scans - Ti(5), Fe(7), Cu (8), Se (12)
#2. calculate their edge DCM location
#3. fit the E vs Bragg RBV with four values, provide fitting results: dtheta, dlatticeSpace


def scanderive(xaxis,yaxis): 

##def plotscan(scan,**kwargs):
#	fp=open(scan,'r')
#	line=fp.readline()
#	length=0
#	TWOTHREE=False	
#	if kwargs.has_key('lines'):
#		length=int(kwargs['lines'])
#	scname=line.split(',')[0][2:]
#	for i in range(0,len(line.split(','))):
#		if line.split(',')[i][:9]==' --xnumst':
#			print i, line.split(',')[i], line.split(',')[i].split('=')[1]
#			length=int(line.replace('\n','').split(',')[i].split('=')[1])
#		if line.split(',')[i][:9]==' --config' and not kwargs.has_key('lines'):
#			tmp=subprocess.check_output(['wc','-l',line.replace('\n','').split(',')[i].split('=')[1]])
#			length=int(tmp.split()[0])
#			TWOTHREE=True
#	if length==0:
#		print "failed to find length"
#		return 2
#	fp.readline()
#	fp.readline()
##	fp.readline()
#	offset=fp.tell()
#	xaxis=numpy.zeros(length)
#	yaxis=numpy.zeros(length)
#	i0=numpy.zeros(length)
# 
#	if kwargs.has_key('x'):
#		x=kwargs['x']
#	else:
#		x=2
#	if kwargs.has_key('y'):
#		y=kwargs['y']
#	else:
#		y=7
#  	if kwargs.has_key('i0'):
#		i0col=kwargs['i0']
#	if kwargs.has_key('Ugap'):
#		ugap=kwargs['Ugap']  
#	if kwargs.has_key('derivative'):
#		dxaxis=numpy.zeros(length-1)
#		dyaxis=numpy.zeros(length-1)
#	fp.seek(offset)
#	for i in range(0,length):
#		line=fp.readline()
#
#		if scname=='srx-scan-slits.py':
#			print line.split()[x]
#			xaxis[i]=float(line.split()[x].strip(','))
#			yaxis[i]=float(line.split()[y].strip(','))
#		else:
#			#print line
#			xaxis[i]=float(line.split()[x])
#			yaxis[i]=float(line.split()[y])
#			if kwargs.has_key('i0'):
#			    i0[i]=float(line.split()[i0col])    
#			    yaxis[i]=yaxis[i]/i0[i]*(-1) 
#       		if kwargs.has_key('Ugap'):
#                     [i]=float(line.split()[ugap])                     
#                     print 'Ugap', ugap 
#	fp.close()
	
	#if data were collected in absoprtion/transmission mode, instead of fluo.
#	if kwargs.has_key('abso'):
#          yaxis=yaxis
#          #print yaxis
#          yaxis=-numpy.log(yaxis)
#	
#	if kwargs.has_key('norm'): 
#          norm0=numpy.average(yaxis[:5])
#          norm1=numpy.average(yaxis[-5:])
#          yaxis=(yaxis-norm0)/(norm1-norm0)       

#	if kwargs.has_key('derivative'):
    
    length=len(xaxis)
    dxaxis=xaxis[0:-1]
    dyaxis=yaxis[0:-1]
    
    for i in range(0,length-1):
        dxaxis[i]=(xaxis[i]+xaxis[i+1])/2.
        dyaxis[i]=(yaxis[i+1]-yaxis[i])/(xaxis[i+1]-xaxis[i])
		#print "Deriv. max value is ",dyaxis.max()," at ", dxaxis[dyaxis.argmax()]
		#print "Deriv. min value is ",dyaxis.min()," at ", dxaxis[dyaxis.argmin()]
		#pyplot.plot(dxaxis,dyaxis,'+')
    p=pyplot.plot(dxaxis,dyaxis*(-1),'-')
    #make the useoffset = False
    ax = pyplot.gca()
    ax.ticklabel_format(useOffset=False)
    #edge = dxaxis[dyaxis.argmin()]
    edge = dxaxis[dyaxis.argmin()]

    return p, dxaxis,dyaxis, edge

fitfunc = lambda pa, x: 12.3984/(2*pa[0]*numpy.sin((x+pa[1])*numpy.pi/180))  
errfunc = lambda pa, x, y: fitfunc(pa,x) - y

  
scandir='/nfs/xf05id1/data/'


#try to work out automatic energy calibration for HDCM
energyDic={'Cu':8.979, 'Se': 12.658, 'Zr':17.998, 'Nb':18.986, 'Fe':7.112, 
           'Ti':4.966, 'Cr': 5.989, 'Co': 7.709}

#datalogDic={'Cu':'11_42', 'Se':'14_31', 'Fe':'14_41', 'Co':'17_56', 'Ti':'15_56'}
#datalogDic={'Cu':'11_42', 'Ti':'15_56'}
#dateDic={'Cu':'2015/4/6', 'Se':'2015/3/23', 'Fe':'2015/2/21', 'Co':'2015/2/21', 'Ti':'2015/4/6'}
#BraggRBVDic={'Cu':12.5, 'Se':8.7, 'Co': 14.6, 'Fe':15.9, 'Ti':23.0}

#2015 cycle 1 calibration
#dateDic={'Se':'2015/4/10', 'Cu':'2015/4/10', 'Fe':'2015/4/10', 'Ti':'2015/4/10'}
#datalogDic={'Ti':'20_19', 'Fe':'20_37', 'Cu':'20_55', 'Se':'22_8'}

#2015 cycle 2 calibration
dateDic={'Ti':'2015/6/13', 'Fe':'2015/6/13', 'Cu':'2015/6/13', 'Se':'2015/6/13'}
datalogDic={'Ti':'21_15', 'Fe':'21_51', 'Cu':'22_4', 'Se':'22_39'}

#2015 cycle 2 calibration repeat
dateDic={'Ti':'2015/6/17', 'Fe':'2015/6/17', 'Cu':'2015/6/17', 'Se':'2015/6/17'}
datalogDic={'Ti':'17_1', 'Fe':'17_19', 'Cu':'17_46', 'Se':'17_59'}

dateDic={'Ti':'2015/10/5', 'Fe':'2015/10/5', 'Cu':'2015/10/5', 'Se':'2015/10/5'}
datalogDic={'Ti':'20_58', 'Fe':'20_7', 'Cu':'19_47', 'Se':'20_33'}
roiDic={'Ti':[433, 488], 'Cr':[520, 550], 'Fe':[620,640], 'Cu':[770,815], 'Se':[1101,1138]}


datalogDic={'Ti':'2015_11_10_0_8', 
            'Cr':'2015_11_9_23_48',
            'Fe':'2015_11_10_0_24',
            'Cu':'2015_11_10_0_53',
            'Se':'2015_11_10_1_12'
            }


BraggRBVDic={}
fitBragg=[]
fitEnergy=[]


for element in datalogDic:
    print 'element:', element
    print 'K-edge:', energyDic[element]
    print 'data:', datalogDic[element]
    #scanfile = scandir+dateDic[element]+'/log_'+datalogDic[element]+'_srx-coord-energy.py.txt'
    
    rawx,rawy = xa.x3toAthena(fileprefix=datalogDic[element], roil=roiDic[element][0], roih=roiDic[element][1], 
                                plot=True, normalization=True, savetoAthena=False, returnarray=True, sampleinfo=element,
                                xbragg=True)
    
    
    p, xaxis, yaxis, edge = scanderive(rawx,rawy)    
    
    #p, xaxis, yaxis, edge = plotscan(scanfile, x=1, y=9, i0=8, abso=True, norm=True, derivative=True)
    #p, xaxis, yaxis, edge = plotscan(scanfile, x=1, y=9, i0=8, abso=True, norm=True)
    BraggRBVDic[element] = round(edge,3)
    print 'Edge position is at Braggg RBV', BraggRBVDic[element]
    pyplot.show(p)
    
    fitBragg.append(BraggRBVDic[element])
    fitEnergy.append(energyDic[element])

#print BraggRBVDic
#print fitBragg
#print fitEnergy
#
#fitfunc = lambda dSi111, dtheta, fitBragg: 12.3984/(2*dSi111*numpy.sin(numpy.pi+dtheta))
#errfunc = lambda dSi111, dtheta, fitBragg, fitEnergy: fitfunc(dSi111, dtheta, fitBragg) - fitEnergy
#
#dSi111 =   
##

fitEnergy=numpy.sort(fitEnergy)
fitBragg=numpy.sort(fitBragg)[-1::-1]

guess = [3.1356, 0.32]
fitted_dcm, success = sp.optimize.leastsq(errfunc, guess, args = (fitBragg, fitEnergy))

print '(111) d spacing:', fitted_dcm[0]
print 'Bragg RBV offset:', fitted_dcm[1]
print 'success:', success


newEnergy=fitfunc(fitted_dcm, fitBragg)

print fitBragg
print newEnergy

pyplot.figure(1)    
pyplot.plot(fitBragg, fitEnergy,'b^', label = 'raw scan')
bragg = numpy.linspace(fitBragg[0], fitBragg[-1], 200)
pyplot.plot(bragg, fitfunc(fitted_dcm, bragg), 'k-', label = 'fitting')
#plt.show(p)
pyplot.legend()
pyplot.xlabel('Bragg RBV (deg)')
pyplot.ylabel('Energy(keV)')

pyplot.show() 
print '(111) d spacing:', fitted_dcm[0]
print 'Bragg RBV offset:', fitted_dcm[1]


