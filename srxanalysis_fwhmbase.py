import numpy
import string
from matplotlib import pyplot
import subprocess 

def aeq(a,b,tol):
    return abs(a-b) <= (abs(a)+abs(b))/2 * tol

def plotscan(scan,**kwargs):
    fp=open(scan,'r')
    line=fp.readline()
    length=0
    TWOTHREE=False  
    if kwargs.has_key('lines'):
        length=int(kwargs['lines'])
    scname=line.split(',')[0][2:]
    for i in range(0,len(line.split(','))):
        if line.split(',')[i][:9]==' --xnumst':
#            print i, line.split(',')[i], line.split(',')[i].split('=')[1]
            length=int(line.replace('\n','').split(',')[i].split('=')[1])
        if line.split(',')[i][:9]==' --config' and not kwargs.has_key('lines'):
            tmp=subprocess.check_output(['wc','-l',line.replace('\n','').split(',')[i].split('=')[1]])
            length=int(tmp.split()[0])
            TWOTHREE=True
    if length==0:
        print "failed to find length"
        return 2
    fp.readline()
    fp.readline()
    offset=fp.tell()
    while(fp.readline()[0]=='#'):
        offset=fp.tell()
    xaxis=numpy.zeros(length)
    yaxis=numpy.zeros(length)
    if kwargs.has_key('x'):
        x=kwargs['x']
    else:
        x=2
    if kwargs.has_key('y'):
        y=kwargs['y']
    else:
        y=7
    if kwargs.has_key('derivative'):
        dxaxis=numpy.zeros(length-1)
        dyaxis=numpy.zeros(length-1)
    fp.seek(offset)
    for i in range(0,length):
        line=fp.readline()
        if scname=='srx-scan-slits.py':
            print line.split()[x]
            xaxis[i]=float(line.split()[x].strip(','))
            yaxis[i]=float(line.split()[y].strip(','))
#        elif scname[-19:]=='srx-gc-slit-scan.py':
#           print line.split()[x]
#           xaxis[i]=float(line.split()[x].strip(','))
#           yaxis[i]=float(line.split()[y].strip(','))
        else:
            xaxis[i]=float(line.split()[x])
            yaxis[i]=float(line.split()[y])
    fp.close()
    if kwargs.has_key('derivative'):
        for i in range(0,length-1):
            dxaxis[i]=(xaxis[i]+xaxis[i+1])/2.
            dyaxis[i]=(yaxis[i+1]-yaxis[i])/(xaxis[i+1]-xaxis[i])
        print "Deriv. max value is ",dyaxis.max()," at ", dxaxis[dyaxis.argmax()]
        print "Deriv. min value is ",dyaxis.min()," at ", dxaxis[dyaxis.argmin()]
        p=pyplot.plot(dxaxis,dyaxis,'+')
        pyplot.show()
        return dxaxis,dyaxis
    elif kwargs.has_key('fwhm'):
        ybase=8.43E-10
        nx=numpy.linspace(xaxis[0],xaxis[-1],10000)
        yaxis=numpy.abs(yaxis-ybase)
        ny=numpy.interp(nx,xaxis,yaxis)
        width=list()
        tot=0.
        for i in range(0,len(nx)):
            tot=tot+ny[i]
            if aeq(ny[i],ny.max()/2.,0.01):
                width.append(nx[i])
        try:
            rstr='FWHM: ', repr(width[-1]-width[0]), 'Intensity: ', repr(tot)
            return rstr
        except IndexError:
            print 'no points found within tolerance'
    else:
        print "Signal max value is ",yaxis.max()," at ", xaxis[yaxis.argmax()]
        print "Signal min value is ",yaxis.min()," at ", xaxis[yaxis.argmin()]
        p=pyplot.plot(xaxis,yaxis,'+')
        pyplot.show()
        return xaxis,yaxis

