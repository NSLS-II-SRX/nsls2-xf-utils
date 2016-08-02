# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 18:47:43 2016

@author: xf05id1
"""
import h5py
import numpy
import matplotlib.pyplot as plt
import glob, os

def sum_element(h5filepath = None, h5filename = None, element = 'Cu_K',
                       i0f = 1e8, fitdata = 'detsum', i0name = 'current_preamp_ch2'):
                           
    h5file = h5py.File(h5filepath+h5filename, 'r')
    
    fitnum='/xrfmap/'+fitdata+'/xrf_fit'
    fitname='/xrfmap/'+fitdata+'/xrf_fit_name'
    

    xrf_fit_name = numpy.array(h5file[fitname])
    fit_index = numpy.where(xrf_fit_name == element)[0][0]
    #xrf_fit = numpy.array(h5file[fitnum])
    fit_array = numpy.array(h5file[fitnum])[fit_index]
        
    scalers_name = numpy.array((h5file['/xrfmap/scalers/name']))
    i0_index = numpy.where(scalers_name == i0name)[0][0]
    i0 = numpy.array(h5file['/xrfmap/scalers/val'])[:,:,i0_index]
    #i0 = numpy.squeeze(i0)
    
    fit_norm = fit_array/(i0*i0f)
    
    element_sum = sum(sum(fit_norm))            
    h5file.close()
    
    return element_sum, fit_norm
    
def sum_element_evolution(h5filepath = None, h5filename_list = None, element = 'Cu_K', i0f = 1e8,
                          fitdata = 'detsum', show_plot = True):
    element_sum_array = []
    for h5filename in h5filename_list:
        if h5filename[-3:] != '.h5':
            h5filename = h5filename+'.h5'
        element_sum, fit_norm = sum_element(h5filepath = h5filepath, h5filename = h5filename, 
                                  element = element, i0f = i0f,
                                  fitdata = fitdata)
        element_sum_array.append(element_sum)
       
    if show_plot:
        plt.plot(range(len(h5filename_list)), element_sum_array) 
        plt.show()
    
    return element_sum_array
        
def export_elementct_txt(h5filepath = None, h5filename = None,  
                       i0f = 1e8, fitdata = 'detsum', i0name = 'current_preamp_ch2',
                       element_list = ['Cr_K', 'Fe_K', 'Ni_K'], 
                       outtxtdir = None, outtxtfilename = None):
    fit_norm_list = []
    
    if outtxtdir is None:
        outtxtdir = h5filepath
    if outtxtfilename is None:
        outtxtfilename = 'elementct_' + h5filename.split('.')[0] + '.txt'
    else:
        if outtxtfilename[-4:] != '.txt':
            outtxtfilename = outtxtfilename+'.txt'
                           
    for element in element_list:
        element_sum, fit_norm = sum_element(h5filepath = h5filepath, h5filename = h5filename, 
                                element = element, i0f = i0f,
                                fitdata = fitdata, i0name = i0name)
        fit_norm_list.append(fit_norm.flatten())
    fit_norm_list = numpy.array(fit_norm_list)
        
    f = open(outtxtdir + outtxtfilename, 'w')      
    
    print('writing file: ' + outtxtdir + outtxtfilename)
    for element in element_list:
        f.write(element + '\t')
    f.write('\n')
    
    for i in range(fit_norm_list.shape[1]):
        #print(i)
        for idx, element in enumerate(element_list):
            f.write(str(fit_norm_list[idx][i]) + '\t')
        f.write('\n')
        
    f.close
    print('done.')
        
    return fit_norm_list
    
def batchdir_export_elementct_txt(working_dir = None,  
                                  i0f = 1e8, fitdata = 'detsum', i0name = 'current_preamp_ch2',
                                  element_list = ['Cr_K', 'Fe_K', 'Ni_K'], 
                                  outtxtdir = None):
    if outtxtdir is None:
        outtxtdir = working_dir
        
    os.chdir(working_dir)
    print('change current directory to')
    print(working_dir)
    for filename in glob.glob('*.h5'):
        print(filename)
        try: export_elementct_txt(h5filepath = working_dir, h5filename = filename,  
                       i0f = i0f, fitdata = fitdata, i0name = i0name,
                       element_list = element_list, 
                       outtxtdir = outtxtdir, outtxtfilename = None)
        except: print('Cannot fit this scan: '+filename)
                                      
    
    