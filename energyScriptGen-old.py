# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 18:53:22 2015
Setup energy tmp file for energy coordinate scan script written by Garth
@author: ycchen
"""

from __future__ import print_function
import numpy
import SRXenergy

def genEtmp(filename, Ustart=11.28, Uend=11.38, Bstart=12.44, Bend=12.34, 
            cgap = 4.0, numpt=51,
            filedir='/nfs/xf05id1/energyScanConfig/'):
    '''
    provide the start & end positions for undulator gap and Bragg angel
    file will be saved to the indicated file directory and file name
    '''
    
    print(filedir)
    out=open( filedir + filename + '.text','w')
    Ugap=numpy.linspace(Ustart, Uend,num=numpt)
    Bragg=numpy.linspace(Bstart, Bend, num=numpt)
    for i in xrange(0,numpt):
#        str="%(a)6.4f %(b)6.3f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}
        str="%(a)6.4f %(b)6.4f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}

        out.write(str)
    out.close()

    
def genEtmpByE(filename, Estart=8.0, Eend=9.0, harmonicVal = 3, cgap = 4.0, numpt=51,
            filedir='/nfs/xf05id1/energyScanConfig/'):
    '''
    provide the start & end positions for energy
    file will be saved to the indicated file directory and file name
    '''
    
    print(filedir)
    out=open( filedir + filename + '.text','w')
    
    Bstart, C2X, Ustart=SRXenergy.EtoAll(Estart, harmonic = harmonicVal)    
    Bend, C2X, Uend=SRXenergy.EtoAll(Eend, harmonic = harmonicVal)
    
    Ugap=numpy.linspace(Ustart, Uend,num=numpt)
    Bragg=numpy.linspace(Bstart, Bend, num=numpt)
    for i in xrange(0,numpt):
#        str="%(a)6.4f %(b)6.3f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}
        str="%(a)6.4f %(b)6.4f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}

        out.write(str)
    out.close()

def genEbyEwC2X(filename, Estart=8.0, Eend=9.0, harmonicVal = 3, XoffsetVal=25.2709, Estep=.001, numEpts=None, display=False,
            filedir='/nfs/xf05id1/energyScanConfig/'):
    '''
    provide the start & end positions for energy in keV, correct c2x for each step using values calculated by SRXenergy.EtoAll
    user can specify either Estep or numEpts; if numEpts is specified, Estep will be ignored; if numEpts is not specified, Estep will be used (default = 1 eV)
    when display is True, bragg, ugap and c2x values will be printed for each energy point; default = False
    filename needs to be string type
    file will be saved to the indicated file directory and file name
    '''
    
    print(filedir)
    out=open( filedir + filename + '.text','w')
    
    print('start E:')
    Bstart, C2X, Ustart=SRXenergy.EtoAll(Estart, harmonic = harmonicVal,Xoffset=XoffsetVal)    
    print('end E:')    
    Bend, C2X, Uend=SRXenergy.EtoAll(Eend, harmonic = harmonicVal,Xoffset=XoffsetVal)
    
#    Ugap=numpy.linspace(Ustart, Uend,num=numpt)
#    Bragg=numpy.linspace(Bstart, Bend, num=numpt)
    
    if numEpts == None:    
        nume=int((Eend-Estart)/Estep+1) #number of energy points
    else: 
        nume=numEpts
    print(nume)
    pt=1
    elist=[]
    for e in numpy.linspace(Estart, Eend, num=nume):
        elist.append(e)        
        if display:
            print('Energy point number:',pt)
        braggtar, c2xtar, ugaptar=SRXenergy.EtoAll(e, harmonic = harmonicVal, Xoffset=XoffsetVal, show=display) 
#        str="%(a)6.4f %(b)6.3f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}
        str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xtar}
        out.write(str)
        pt=pt+1
    print('energy points:', elist)
    print('total energy number of point:', nume)
    print('energy step size:', (elist[1]-elist[0])*1000, 'eV; ', (elist[1]-elist[0]), 'keV' )
    out.close()

def genElin(filename, Estart=8.0, Eend=9.0, harmonicVal = 3, cgapstart= 3.0, cgapend=4.0, numpt=51,
            filedir='/nfs/xf05id1/energyScanConfig/'):
    '''
    provide the start & end positions for energy
    file will be saved to the indicated file directory and file name
    '''
    
    print(filedir)
    out=open( filedir + filename + '.text','w')
    
    Bstart, C2X, Ustart=SRXenergy.EtoAll(Estart, harmonic = harmonicVal)    
    Bend, C2X, Uend=SRXenergy.EtoAll(Eend, harmonic = harmonicVal)
    
    Ugap=numpy.linspace(Ustart, Uend,num=numpt)
    Bragg=numpy.linspace(Bstart, Bend, num=numpt)
    cgap=numpy.linspace(cgapstart, cgapend, num=numpt)
    for i in xrange(0,numpt):
#        str="%(a)6.4f %(b)6.3f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}
        str="%(a)6.4f %(b)6.4f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap[i]}

        out.write(str)
    out.close()

def genEtmpByErange(filename, E0=8.0, E1=8.1, E2 =8.2, E3 = 8.3, harmonicVal = 3, cgap = 4.0, numpt1=51, numpt2= 10, numpt3 = 50,
            filedir='/nfs/xf05id1/energyScanConfig/'):
    '''
    provide the start & end positions for energy
    four different energy ranges, set different number of points
    E0-E1:numpt1, E1-E2:numpt2, E2-E3:numpt3, 
    file will be saved to the indicated file directory and file name
    '''
    
    print(filedir)
    out=open( filedir + filename + '.text','w')

    #first range
    Bstart, C2X, Ustart=SRXenergy.EtoAll(E0, harmonic = harmonicVal)    
    Bend, C2X, Uend=SRXenergy.EtoAll(E1, harmonic = harmonicVal)
    
    Ugap=numpy.linspace(Ustart, Uend,num=numpt1)
    Bragg=numpy.linspace(Bstart, Bend, num=numpt1)
    for i in xrange(0,numpt1):
        str="%(a)6.4f %(b)6.4f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}
        out.write(str)

    #second range
    Bstart, C2X, Ustart=SRXenergy.EtoAll(E1, harmonic = harmonicVal)    
    Bend, C2X, Uend=SRXenergy.EtoAll(E2, harmonic = harmonicVal)
    
    Ugap=numpy.linspace(Ustart, Uend,num=numpt2)
    Bragg=numpy.linspace(Bstart, Bend, num=numpt2)
    for i in xrange(1,numpt2):
        str="%(a)6.4f %(b)6.4f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}
        out.write(str)

    #third range
    Bstart, C2X, Ustart=SRXenergy.EtoAll(E2, harmonic = harmonicVal)    
    Bend, C2X, Uend=SRXenergy.EtoAll(E3, harmonic = harmonicVal)
    
    Ugap=numpy.linspace(Ustart, Uend,num=numpt3)
    Bragg=numpy.linspace(Bstart, Bend, num=numpt3)
    for i in xrange(1,numpt3):
        str="%(a)6.4f %(b)6.4f %(c)6.3f\n"%{"a":Bragg[i], "b":Ugap[i], "c":cgap}
        out.write(str)

    out.close()
    
#def getE
    
#def getBragg( )