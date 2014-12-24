import os
import sys
import itertools
import collections
import io

import numpy as np
import pandas as pd


def output_txtfile_to_DataFrame(readfrom = './zz-output-onlysw-now.txt'):
    '''
    Converts Yi-Hsuan\'s RRTMG-SW\'s output in zz-output-onlysw-now.dat to
    a Pandas DataFrame
    '''
    columns = ['pressure', 'dflux', 'uflux', 'netflx', 'hr']
    
    with open(readfrom, mode = 'r', encoding = 'utf-8') as file:
        c = file.read()

    lines = [line for line in c.split('hr')[-1].split('\n') \
             if line and not line.isspace()][: -4]

    toprow = lines[0].split()[1:] + [np.nan]
    restrows = [lev.split()[1:] + [lay] \
               for lay, lev in itertools.zip_longest(*(2 * [iter(lines[1:])]))]

    data = np.array([toprow] + restrows).astype('f8')
    return pd.DataFrame(data = data[:: -1], columns = columns).\
                      sort_index(ascending = False)


def OUTPUT_RRTM_to_pandasPanel(readfrom = '', cooling_rate = False,
                               signed_fluxes = False):

    '''
    Read and convert OUTPUT_RRTM file from RRTMG-SW to Pandas
    Panel object
    '''
    with open(readfrom, mode = 'r', encoding = 'utf-8') as file:
        c = file.read()

    content_wbs = [s.strip()
                   for s in c.split('\x0c')[1: -1] if s and not s.isspace()]

    data = {}
    for content_wb in content_wbs:
        l1 = content_wb.split('\n', maxsplit = 1)[0].split()
        V1, V2 = float(l1[1]), float(l1[3])
        df = pd.read_csv(io.StringIO(content_wb),
                         header = None, skiprows = 3, index_col = [0],
                         sep = r'\s+')
        df.index.name = None
        data[(V1, V2)] = df

    pnl = pd.Panel(data)

    if cooling_rate:
        pnl.values[:, :, -1] *= -1
        rate_label = 'cooling_rate'
    else:
        rate_label = 'heating_rate'

    if signed_fluxes:
        pnl.values[:, :, 1] *= -1
        pnl.values[:, :, 5] = pnl.values[:, :, 1] + pnl.values[:, :, 4]

    pnl.minor_axis = ['pressure', 'flux_up',
                      'flux_difdown', 'flux_dirdown',
                      'flux_down', 'net_flux', rate_label]
    return pnl
        
    
        
