import os
import sys
import itertools
import collections
import io

import numpy as np
import pandas as pd


def output_txtfile_to_DataFrame(readfrom = './tt-output-now.dat'):
    '''
    Converts CLIRAD-SW\'s output in tt-output-now.dat to
    a Pandas DataFrame
    '''
    columns = ['pressure', 'fdnto', 'fupto', 'flx', 'heating_rate']
    with open(readfrom, mode = 'r', encoding = 'utf-8') as file:
        c = file.read()

    lines = [line for line in c.split('(C/day)')[-1].split('\n') \
             if line and not line.isspace()][: -6]

    toprow = lines[0].split()[1:] + [np.nan]
    restrows = [lev.split()[1:] + [lay] \
               for lay, lev in itertools.zip_longest(*(2 * [iter(lines[1:])]))]

    data = np.array([toprow] + restrows).astype('f8')
    return pd.DataFrame(data = data[:: -1], columns = columns).\
                      sort_index(ascending = False)
    


def OUTPUT_CLIRAD_to_PandasPanel(readfrom = 'OUTPUT_CLIRAD.dat',
                                 cooling_rate = False,
                                 signed_fluxes = False):
    '''
    Reads output data from CLIRAD into a Pandas Panel of dimensions
    (wavenumber bands, pressure, [flux up, flux down, net flux, heating rate])
    '''
    with open(readfrom, mode = 'r', encoding = 'utf-8') as f:
        c = f.read()

    content_wbs = (s.strip() for s in c.split('WAVENUMBER BAND:')\
                   if s and not s.isspace())

    data = {}
    for content_wb in content_wbs:
        id_wb = int(content_wb.split(maxsplit = 1)[0])
        df_wb = pd.read_csv(io.StringIO(content_wb), \
                skiprows = 3, header = None, index_col = [0], \
                sep = r'\s+')
        df_wb.index.name = None #this removes a '0' name for dataframe index
        data[id_wb] = df_wb

    pnl = pd.Panel(data)

    if cooling_rate:
        pnl.values[:, :, -1] *= -1
        rate_label = 'cooling_rate'
    else:
        rate_label = 'heating_rate'

    if signed_fluxes:
        pnl.values[:, :, 1] *= -1
        pnl.values[:, :, 3] = pnl.values[:, :, 1] + pnl.values[:, :, 2]
    
    pnl.minor_axis = ['pressure', 'flux_up', 'flux_down', 'net_flux', rate_label]
    return pnl
        
        


    
