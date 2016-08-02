# -*- coding: utf-8 -*-
"""
Created on Sun Jun 12 20:22:08 2016

@author: xf05id1
"""
from pyxrf.api import *
from databroker.databroker import DataBroker as db, get_table, get_events

def get_x3data(scanid, return_allch = False):
    x3data = get_table(db[scanid], fields=['xs_settings_ch1', 'xs_settings_ch2', 'xs_settings_ch3'])
    energy = get_table(db[scanid], ['energy_energy'])
    
    x3datasum = x3data['xs_settings_ch1'] +  x3data['xs_settings_ch2'] +  x3data['xs_settings_ch3'] 
    
    if return_allch:
        return energy, x3datasum, x3data
    else:    
        return energy, x3datasum
