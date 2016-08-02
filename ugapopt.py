from matplotlib import pyplot
import numpy
#import srxmcaEnergyCal
import string
import sys
import math
import scipy as sp
import scipy.optimize


def peakfit(fileprefix=None, xcol = 3-1, ycol = 6-1, a= 15000., b = 8., c = 0.05  ):

    if fileprefix == None:
        print "please provide a fileprefix as indicated in Xspress3 screen. E.g. '2015_10_25_21_14'"
        sys.exit()
    if fileprefix[-1] == '_':
        fileprefix=fileprefix[0:-1]
        
    print 'input file:', fileprefix

    #load i0 and energy from text file
    dirf = string.split(fileprefix, sep='_')
    textfiledir = '/nfs/xf05id1/data/'+ dirf[0] + '/' + dirf[1] + '/' + dirf[2] + '/' 
    textfilename = 'log_' + fileprefix + '_srx-scan-1d-ad-e.py.txt'
    #print textfilename
    textfile=textfiledir+textfilename
    print 'reading x,y values from:', textfile


    xarray=[]
    yarray=[]

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
                xpt = float(a[xcol])
                ypt = float(a[ycol])

                xarray.append(xpt)   
                yarray.append(ypt)


    xarray = numpy.array(xarray)
    yarray = numpy.array(yarray)
    
    print xarray
    print yarray
 
 
   
#    fitfunc = lambda pa, x: pa[1]*x+pa[0]  
#    errfunc = lambda pa, x, y: fitfunc(pa,x) - y

#fitting
    fitfunc = lambda pa, x: pa[0]*numpy.exp(-((x-pa[1])**2)/(2*((pa[2])**2)))  
    #fitfunc = lambda pa, x: pa[0]*numpy.exp(-((x-pa[1])*(x-pa[1]))/(2*pa[2]*pa[2])) 
    #fitfunc = lambda pa, x: pa[1]*x+pa[0]          
    errfunc = lambda pa, x, y: fitfunc(pa,x) - y
    
    guess = [a, b, c]
    fit, success = sp.optimize.leastsq(errfunc, guess, args = (xarray, yarray))    
    
    #fwhm = 2*(2*math.log(2))**(0.5)*fit[2]
    

    pyplot.figure(1)
    pyplot.plot(xarray, yarray, 'b+')
    pyplot.plot(xarray, fit[0]*numpy.exp(-((xarray-fit[1])**2)/(2*((fit[2])**2)))  , 'k-')
    
    pyplot.title(fileprefix)
    pyplot.xlabel('x')
    pyplot.ylabel('y')

    pyplot.show() 

    print fwhm     