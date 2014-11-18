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


        
def sum_OUTPUT_RRTM_over_wave_numbers(readfrom = './OUTPUT_RRTM',
                                      V1 = 0, V2 = 3000):
    '''
    Sum the fluxes and cooling rates over wave number bands
    between V1 and V2.  If V1 and V2 do not match any wave number band\'s
    boundaries, they will be rounded to the closest boundaries.
    '''
    dpanel = OUTPUT_RRTM_to_pandasPanel(readfrom = readfrom,
                                        cooling_rate = True,
                                        signed_fluxes = True)
    V1s, V2s = (lev.values for lev in dpanel.items.levels)
    item1, item2 = (np.abs(vs - v).argmin() \
                    for vs, v in zip([V1s, V2s], [V1, V2]))
    flux_cor_tot = dpanel.ix[item1: item2, :, \
                             ['flux_up', 'flux_down', \
                              'net_flux', 'cooling_rate']].\
                              sum(axis = 'items')
    pressure = dpanel.ix[dpanel.items[0], :, 'pressure']
    return pd.concat([pressure, flux_cor_tot], axis = 1)
