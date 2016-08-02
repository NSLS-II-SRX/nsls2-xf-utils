from __future__ import print_function
from matplotlib import pyplot
import numpy
#import srxmcaEnergyCal
import string
import sys
import math
import scipy as sp
import scipy.optimize



def dataread(fileprefix=None, xcol = 2, ycol = 5, scriptname = 'srx-scan-1d-ad-e-upv.py', 
             printarray = False, nodate = False, chalist = [',', '(',')','[',']',':']):

    '''
    nodate = True: year, month and date will be removed from the prefix when reading the file
    chalist = [',' '[', '('] a list of charaters to be replaced by space    
    
    
    '''

    if fileprefix == None:
        print("please provide a fileprefix as indicated in Xspress3 screen. E.g. '2015_10_25_21_14'")
        sys.exit()
    if fileprefix[-1] == '_':
        fileprefix=fileprefix[0:-1]
        
    print ('input file:'+ fileprefix)

    #load i0 and energy from text file
    dirf = string.split(fileprefix, sep='_')

    textfiledir = '/nfs/xf05id1/data/'+ dirf[0] + '/' + dirf[1] + '/' + dirf[2] + '/' 
    #textfiledir = 'C:\\data\\SRX\\nfs\\'+ dirf[0] + '\\' + dirf[1] + '\\' + dirf[2] + '\\' #only for testing on laptop  

    if nodate == True:
        fileprefix = dirf[3]+'_'+dirf[4]

    textfilename = 'log_' + fileprefix + '_' + scriptname + '.txt'
    
    #print textfilename
    textfile=textfiledir+textfilename
    print ('reading x,y values from:'+textfile)


    xarray=[]
    yarray=[]

    scanproperty = {}

    with open(textfile, 'r') as f:
        #line=f.readline()
        #line=f.readline()
        #line=f.readline()
        while True:
            line=f.readline()
            
            if len(line)>0:            
                if line[1] == '@':
                    
                    line=line.replace('=', ' ')
                    a=string.split(line[2:-1])
                    #print len(a)
                    for i in xrange(len(a)/2):
                        scanproperty[a[i*2]] = a[i*2+1]   
                
            #print line
            for ch in chalist: 
                #print ch
                line=line.replace(ch, ' ')
            #print line

            
            if not line: break
            if line[0] != '#':
                #print line
                a=string.split(line)
                #print a
                xpt = float(a[xcol])
                ypt = float(a[ycol])

                xarray.append(xpt)   
                yarray.append(ypt)


    xarray = numpy.array(xarray)
    yarray = numpy.array(yarray)

    if printarray == True:  
        print('xarray:'+str(xarray))
        print('yarray:'+str(yarray))


    f.close()
    return xarray, yarray, scanproperty


def peakfit_gaussian(xarray = None, yarray = None,  a= 15000., b = 8., c = 0.05,
                     scanid = 'unknown scan', bkgsub = True, bkga = -19912, bkgb = 161928,
                     fitxrange = None, reverse = True, showplot = True):

    '''
    bkgsub = Ture: substract a linear fit with  y = bkga*x + bkgb
    reverse = True: xarray value is decreasing, typical for energy scan using Bragg
    fitxrange = [minx, maxx] in the unit of xarray    
    
    a, b, c used as initial guess of the gaussian fitting
    y =  a*numpy.exp(-((x-b)**2)/(2*((c**2)))

    fit[0] is final fitted a value
    fit[1] is final fitted b value
    fit[2] is final fitted c value

    return fit[0], fit[1], fit[2]

    '''

    if xarray == None:
        print('need to supply xarray')
        sys.exit()
    if yarray == None:
        print('need to supply yarray')
        sys.exit()
        
    if fitxrange == None:
        minindex, maxindex = 0, -1

    else:
        if reverse == True:
            maxindex = next(i for i,v in enumerate(xarray) if v < fitxrange[0])
            minindex = next(i for i,v in enumerate(xarray) if v < fitxrange[1])
            print('minindex, maxindex ='+str(minindex)+','+ str(maxindex))
        else:
            minindex = next(i for i,v in enumerate(xarray) if v > fitxrange[0])
            maxindex = next(i for i,v in enumerate(xarray) if v > fitxrange[1])
            print('minindex, maxindex ='+str(minindex)+','+ str(maxindex))        
           
    fitxarray = xarray[minindex:maxindex] 
    fityarray = yarray[minindex:maxindex]
        
#fitting
    if bkgsub == True:
        fitfunc = lambda pa, x: pa[0]*numpy.exp(-((x-pa[1])**2)/(2*((pa[2])**2)))+pa[3]*x+pa[4]
        guess = [a, b, c, bkga, bkgb]

    else:
        fitfunc = lambda pa, x: pa[0]*numpy.exp(-((x-pa[1])**2)/(2*((pa[2])**2)))          
        guess = [a, b, c]

    errfunc = lambda pa, x, y: fitfunc(pa,x) - y
    fit, success = sp.optimize.leastsq(errfunc, guess, args = (fitxarray, fityarray))    
    
    fwhm = 2*(2*math.log(2))**(0.5)*fit[2]
    
    #print result
    print('a, b, c '+str(fit[0])+','+str(fit[1])+','+str(fit[2]))
    print('fwhm ' + str(fwhm))
    print('peak intensity ' + str(fit[0]))  
    
    #plotting part
    
    if showplot == True:
        pyplot.figure()
        pyplot.plot(xarray, yarray, 'b+')
    
        if bkgsub == True:
            pyplot.plot(fitxarray, fit[0]*numpy.exp(-((fitxarray-fit[1])**2)/(2*((fit[2])**2)))  , 'k-')
            pyplot.plot(fitxarray, fit[3]*fitxarray+fit[4]  , 'g-')
            pyplot.plot(fitxarray, fit[0]*numpy.exp(-((fitxarray-fit[1])**2)/(2*((fit[2])**2))) + fit[3]*fitxarray+fit[4] , 'r-')
        else:
            pyplot.plot(fitxarray, fit[0]*numpy.exp(-((fitxarray-fit[1])**2)/(2*((fit[2])**2)))  , 'k-')
        
        pyplot.title(scanid)
        pyplot.xlabel('x')
        pyplot.ylabel('y')
    
        pyplot.show() 

    return fit[0], fit[1], fit[2], fwhm
    
def peakfind (xarray = None, yarray = None, printindex = False, widtherr = 0.01):

    if xarray == None:
        print('need to supply xarray')
        sys.exit()
    if yarray == None:
        print('need to supply yarray')
        sys.exit()
    
    YmaxYvalue = numpy.max(yarray)
    Ymaxindex = numpy.argmax(yarray)
    YmaxXvalue = xarray[Ymaxindex]
    
    print('maximum y, y value = ' + str(YmaxYvalue))
    print('maximum y, x value = ' + str(YmaxXvalue))
    
    if printindex == True:
        print('maximum y, x and y index = '+ str(Ymaxindex))

    widthpt = [0, 0]
    err = [99999999, 99999999]
    for y in yarray[0:Ymaxindex]:
        if abs(y -  YmaxYvalue/2) < err[0]:
            err[0] = abs(y -  YmaxYvalue/2)
            widthpt[0] = y
            #print abs(y -  YmaxYvalue/2), err[0], y

    for y in yarray[Ymaxindex:-1]:
        if abs(y -  YmaxYvalue/2) < err[1]:
            err[1] = abs(y -  YmaxYvalue/2)
            widthpt[1] = y
            
    #print 'widthpt = ', widthpt
    
    widthxpt = [numpy.where(yarray == widthpt[0])[0][0], numpy.where(yarray == widthpt[1])[0][0]]
    #print 'widthxpt = ', widthxpt

    widthxvalue = [xarray[widthxpt[0]], xarray[widthxpt[1]]]
    peakwidth = abs(widthxvalue[1] - widthxvalue[0])
    print('peak width = ' + str(peakwidth))
    print('peak width is defined from ' + str(widthxvalue[0]) + ' to ' + str(widthxvalue[1]))

    return YmaxYvalue, YmaxXvalue, Ymaxindex, peakwidth 
    

    
    
    
    
    
    