import os
import collections
import itertools
import io
import numpy as np
import pandas as pd



def OUTPUT_RRTM_to_pandasPanel(readfrom = '', cooling_rate = False,
                                 signed_fluxes = False):
    '''
    Convert OUTPUT_RADSUM to Pandas Panel Object
    '''
    with open(readfrom, mode = 'r', encoding = 'utf-8') as file:
        c = file.read()

    outrad_dict = collections.OrderedDict({})
    for bandstr in c.split('\x0c')[1: -1]:
        bandstr = bandstr.strip()
        line_band = bandstr.split('\n')[0]
        V1, V2 = (float(V) for V in line_band.split(':')[-1]\
                  .split('cm-1')[0].split('-'))
        item = pd.MultiIndex.from_tuples([(V1, V2),])
        df = pd.read_csv(io.StringIO(bandstr),
                         skiprows = 3,
                         sep = r'\s+', index_col = [0],
                         header = None)
        df.index.name = None
        outrad_dict.update({(V1, V2): df})
        
    dpanel = pd.Panel.from_dict(outrad_dict)

    if cooling_rate:
        dpanel.values[:, :, -1] *= -1
        rate_label = 'cooling_rate'
    else:
        rate_label = 'heating_rate'

    if signed_fluxes:
        dpanel.values[:, : , 1] *= -1
        dpanel.values[:, :, 3] = dpanel.values[:, :, 1] + dpanel.values[:, :, 2]

    dpanel.minor_axis = ['pressure', 'flux_up', 'flux_down', 'net_flux', rate_label]
    return dpanel

        
    

        
