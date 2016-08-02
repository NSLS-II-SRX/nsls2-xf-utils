# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 18:53:22 2015
Setup energy tmp file for energy coordinate scan script written by Garth
@author: ycchen
"""

from __future__ import print_function
import numpy
import SRXenergy
from epics import PV
import SRXpmenergy

c2xRBV=PV('XF:05IDA-OP:1{Mono:HDCM-Ax:X2}Mtr.RBV')   

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

def genE(filename='econfigtest', Estart=8.0, Eend=9.0, harmonicVal = None, XoffsetVal=SRXenergy.XoffsetCurrent, Estep=.001, numEpts=None, 
         display=False, showelist=False, correctC2X=True, c2xfix=None, nosave = False, 
            detuneugap = None,  #future capability
            filedir='/nfs/xf05id1/energyScanConfig/'):
    '''
    previously called: genEbyEwC2X
    provide the start & end positions for energy in keV, correct c2x for each step using values calculated by SRXenergy.EtoAll
    user can specify either Estep or numEpts; if numEpts is specified, Estep will be ignored; if numEpts is not specified, Estep will be used (default = 1 eV)
    when display is True, bragg, ugap and c2x values will be printed for each energy point; default = False
    filename needs to be string type
    file will be saved to the indicated file directory and file name
    
    updated:
        default harmonic will be calculated automatically based on the input energy range
        it'll use the maximum harmonic (smallest u-gap) possible.
        user can still define harmonic if desired.    
    
    [example]
    import escript
    edge=13.035    
    escript.genE(filename='20151024test3', Estart=edge-0.5, Eend=edge+0.5, harmonicVal=7, numEpts=20)
    #OR
    escript.genE(filename='20151024test3', Estart=edge-0.5, Eend=edge+0.5, harmonicVal=7, Estep=0.01)
    '''

    if harmonicVal == None:
        harmonicVal = SRXpmenergy.move(Eend, simulate=True, show=False)
    
    if nosave == False:
        out=open( filedir + filename + '.text','w')        
    
    print('start E:')
    Bstart, C2X, Ustart=SRXenergy.EtoAll(Estart, harmonic = harmonicVal,Xoffset=XoffsetVal)    
    print('end E:')    
    Bend, C2X, Uend=SRXenergy.EtoAll(Eend, harmonic = harmonicVal,Xoffset=XoffsetVal)
        
    if numEpts == None:    
        nume=int(round((Eend-Estart)/Estep+1)) #number of energy points
    else: 
        nume=numEpts
    #print(nume)
    pt=0
    elist=[]
    estep=[]
    c2xnow=c2xRBV.get()
    
    for e in numpy.linspace(Estart, Eend, num=nume):
        pt=pt+1
        elist.append(e)        
        if display:
            print('Energy point number:',pt)
        braggtar, c2xtar, ugaptar=SRXenergy.EtoAll(e, harmonic = harmonicVal, Xoffset=XoffsetVal, show=display)
        
        if correctC2X == True:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xtar}
        elif c2xfix == None:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xnow}
        else:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xfix}
        if pt >= 2:        
            estep.append(elist[pt-1]-elist[pt-2] )

        if nosave == False:
            out.write(str)
    est=numpy.average(numpy.array(estep))
    
    if showelist:
        print('energy points:', elist)
        
    print('total energy number of point:', nume)
    print('energy step size:', est*1000, 'eV; ', est, 'keV' )
    if nosave == False:
        print('--config=\''+filedir+filename+'.text\'')
        out.close()
    else:
        print('nosave = True, file is not saved')
    
def genErange(filename='econfigtest', edge=8.50, E0=-0.1, E1=-0.05, E2 =+0.05, E3 = +0.25, harmonicVal = None,  XoffsetVal=SRXenergy.XoffsetCurrent,
              numEpt1=None, numEpt2= None, numEpt3 = None, Estep1=.002, Estep2 = .001, Estep3 = 0.005,
              correctC2X=True, c2xfix=None, nosave = False,
              display=False, showelist=False,
            filedir='/nfs/xf05id1/energyScanConfig/'):
    '''
    provide the start & end positions for energy
    four different energy ranges, set different number of points
    E0-E1:numpt1, E1-E2:numpt2, E2-E3:numpt3, 
    file will be saved to the indicated file directory and file name
    correct c2x, see genE for the syntax

    updated:
        default harmonic will be calculated automatically based on the input energy range
        it'll use the maximum harmonic (smallest u-gap) possible.
        user can still define harmonic if desired.
    
    [example]
     #using default values: E0=-0.1, E1=-0.05, E2 =+0.05, E3 = +0.25, Estep1=.002, Estep2 = .001, Estep3 = 0.005
     escript.genErange('20151024_Pb_02', edge=13.035, harmonicVal=7)

     #OR specify energy and stepsize
     esscript.Erange('20151024_Pb_03', edge=13.035, E0=-0.2, E1=-0.1, E2 =+0.1, E3 = +0.5, harmonicVal = 7,  Estep1=.005, Estep2 = .002, Estep3 = 0.01)    
    
    '''

    if harmonicVal == None:
#        Eend = edge+E3
#        harmonicVal = SRXpmenergy.move(Eend, simulate=True, show=False)
        Estart = edge+E0
        harmonicVal = SRXpmenergy.move(Estart, simulate=True, show=False)    
    
    if nosave == False:
        out=open( filedir + filename + '.text','w')

    pt = 0
    elist=[]
    c2xnow=c2xRBV.get()

    print('E0:')
    Bstart, C2X, Ustart=SRXenergy.EtoAll(edge+E0, harmonic = harmonicVal)  
    print('E1:') 
    Bend, C2X, Uend=SRXenergy.EtoAll(edge+E1, harmonic = harmonicVal)
    
    #first range   
    if numEpt1 == None:    
        nume=int(round((E1-E0)/Estep1+1)) #number of energy points
    else: 
        nume=numEpt1
    #print(nume)    
    estep=[]

    for e in numpy.linspace(edge+E0, edge+E1, num=nume):
        pt=pt+1
        elist.append(e)  
        if display:
            print('Energy point number:',pt)
        braggtar, c2xtar, ugaptar=SRXenergy.EtoAll(e, harmonic = harmonicVal, Xoffset=XoffsetVal, show=display) 
        if correctC2X == True:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xtar}
        elif c2xfix == None:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xnow}
        else:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xfix}
        if pt >= 2:        
            estep.append(elist[pt-1]-elist[pt-2] )
            #print(estep)
        if nosave == False:
            out.write(str)
    est1=numpy.average(numpy.array(estep))
    #print(len(estep))

    #second range

    print('E1:')
    Bstart, C2X, Ustart=SRXenergy.EtoAll(edge+E1, harmonic = harmonicVal)  
    print('E2:') 
    Bend, C2X, Uend=SRXenergy.EtoAll(edge+E2, harmonic = harmonicVal)

    if numEpt2 == None:    
        nume=int(round((E2-E1)/Estep2+1)) #number of energy points
    else: 
        nume=numEpt2
    #print(nume)    
    estep=[]
    for e in numpy.linspace(edge+E1+Estep2, edge+E2, num=nume-1):
        pt=pt+1
        elist.append(e)  
        if display:
            print('Energy point number:',pt)
        braggtar, c2xtar, ugaptar=SRXenergy.EtoAll(e, harmonic = harmonicVal, Xoffset=XoffsetVal, show=display) 
        if correctC2X == True:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xtar}
        elif c2xfix == None:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xnow}
        else:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xfix}
        estep.append(elist[pt-1]-elist[pt-2] )
        #print(estep)
        out.write(str)
    est2=numpy.average(numpy.array(estep))
    #print(len(estep))

    #third range
    print('E2:')
    Bstart, C2X, Ustart=SRXenergy.EtoAll(edge+E2, harmonic = harmonicVal)  
    print('E3:') 
    Bend, C2X, Uend=SRXenergy.EtoAll(edge+E3, harmonic = harmonicVal)

    if numEpt3 == None:    
        nume=int(round((E3-E2)/Estep3+1)) #number of energy points
    else: 
        nume=numEpt3
    #print(nume)    

    estep=[]
    for e in numpy.linspace(edge+E2+Estep3, edge+E3, num=nume-1):
        pt=pt+1
        elist.append(e)  
        if display:
            print('Energy point number:',pt)
        braggtar, c2xtar, ugaptar=SRXenergy.EtoAll(e, harmonic = harmonicVal, Xoffset=XoffsetVal, show=display) 
        if correctC2X == True:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xtar}
        elif c2xfix == None:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xnow}
        else:
            str="%(bragg)6.4f %(ugap)6.4f %(c2x)6.3f\n"%{"bragg":braggtar, "ugap":ugaptar, "c2x":c2xfix}
        estep.append(elist[pt-1]-elist[pt-2] )
        #print(estep)
        out.write(str)
    est3=numpy.average(numpy.array(estep))
    #print(len(estep))
       
    if showelist:
        print('energy points:', elist)      
    print('total energy number of point:', len(elist))
    print('energy step size 1:', est1*1000, 'eV; ', est1, 'keV' )
    print('energy step size 2:', est2*1000, 'eV; ', est2, 'keV' )
    print('energy step size 3:', est3*1000, 'eV; ', est3, 'keV' )

    if nosave == False:
        print('--config=\''+filedir+filename+'.text\'')
        out.close()
    else:
        print('nosave = True, file is not saved')

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