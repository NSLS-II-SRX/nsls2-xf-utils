# -*- coding: utf-8 -*-
"""
Created on Fri Mar 25 15:28:23 2016

@author: xf05id1
"""

from enaml.qt.qt_application import QApplication #must the first line executed in ipython
import glob, os
from pyxrf.model.command_tools import fit_pixel_data_and_save


def batchfit_dir(working_dir = None, parameter_filename = None, save_tiff = True, save_norm = True):
    os.chdir(working_dir)
    print('change current directory to')
    print(working_dir)
    #wd = '/nfs/xf05id1/userdata/2016_cycle1/300372_Gallaway/xrfbatch/'
    for filename in glob.glob('*.h5'):
        print(filename)
        if save_norm is True:
            try: fit_pixel_data_and_save(working_dir, filename,  
                                param_file_name = parameter_filename,
                                save_tiff = save_tiff, ic_name='current_preamp_ch2')
            except: print('Cannot fit this scan: '+filename)
        else:        
            try: fit_pixel_data_and_save(working_dir, filename,  
                                param_file_name = parameter_filename,
                                save_tiff = save_tiff)
            except: print('Cannot fit this scan: '+filename)
