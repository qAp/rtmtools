import os
import sys
import itertools
import collections
import io

import numpy as np
import pandas as pd
import xray



def output_txtfile_to_DataFrame(readfrom = './tt-output-now.dat'):
    '''
    Converts CLIRAD-SW\'s output in tt-output-now.dat to
    a Pandas DataFrame
    '''
    columns = ['pressure', 'fdnto', 'fupto', 'flx', 'heating_rate']
    with open(readfrom, mode = 'r', encoding = 'utf-8') as file:
        c = file.read()


    lines = [line for line in c.split('******  RESULTS  ******')[-1].split('\n') \
             if line and not line.isspace()] 

    columns = lines[0].split()
    columns[-2] = ' '.join(columns[-2: ])
    columns.pop()
    
    datalines = lines[2: 2 + 2 * 75 + 1] # for 75 layers and 76 levels

    toprow = datalines[0].split()[1:] + [np.nan]
    restrows = [lev.split()[1:] + [lay] \
               for lay, lev in itertools.zip_longest(*(2 * [iter(datalines[1:])]))]

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




def layer_pressure(func):
    def callf(*args, **kwargs):
        ds = func(*args, **kwargs)
        layer_pressure_values = .5 * (ds.coords['level_pressure'][: -1].values \
                                      + ds.coords['level_pressure'][1:].values)
        ds.coords.update({'layer_pressure': (['layer_pressure'], layer_pressure_values)})
        return ds
    return callf


def layer_heating_rate(func):
    def callf(*args, **kwargs):
        ds = func(*args, **kwargs)
        da = ds['heating_rate'].sel(level_pressure=ds.coords['level_pressure'][1:])
        ds['heating_rate'] = (['spectral_band', 'layer_pressure'], da)
        return ds
    return callf


def cooling_rate_option(func):
    def callf(cooling_rate = False, *args, **kwargs):
        ds = func(*args, **kwargs)
        if cooling_rate:
            ds['cooling_rate'] = - ds['heating_rate']
        return ds
    return callf


def signed_fluxes_option(func):
    def callf(signed_fluxes = True, *args, **kwargs):
        ds = func(*args, **kwargs)
        if signed_fluxes:
            ds['flux_up'] *= -1
            ds['net_flux'] = ds['flux_up'] + ds['flux_down']
        return ds
    return callf


@cooling_rate_option
@signed_fluxes_option
@layer_heating_rate
@layer_pressure
def load_OUTPUT_CLIRAD(readfrom = 'OUTPUT_CLIRAD.dat'):
    '''
    Reads output data from CLIRAD into a Pandas Panel of dimensions
    (wavenumber bands, pressure, [flux up, flux down, net flux, heating rate])
    '''
    with open(readfrom, mode = 'r', encoding = 'utf-8') as f:

        c = f.read()

    content_wbs = (s.strip() for s in c.split('WAVENUMBER BAND:')\
                   if s and not s.isspace())

    band_numbers = []
    dfs = []
    for content_wb in content_wbs:
        id_wb = int(content_wb.split(maxsplit = 1)[0])
        df_wb = pd.read_csv(io.StringIO(content_wb), \
                skiprows = 3, header = None, \
                sep = r'\s+')
        df_wb.drop(0, axis = 1, inplace = True)
        df_wb.set_index(1, inplace = True)
        df_wb.columns = ['flux_up', 'flux_down', 'net_flux', 'heating_rate']
        band_numbers.append(id_wb)
        dfs.append(df_wb)

    df = pd.concat(dfs, keys = band_numbers, names = ['spectral_band', 'level_pressure'])

    ds = xray.Dataset.from_dataframe(df)

    return ds

    

        
        


def load_clirad_solirgpts(fpath, signed_fluxes = False, cooling_rate = False):
    '''
    Loads into an Xray Dataset the fluxes and heating rate output from CLIRAD-SW
    for all solir spectral bands, all g-points, and all atmosphere layers.
    INPUT:
    fpath --- path of headered csv files where the columns are:
    spectral band index
    g-point index
    atmosphere level index
    atmosphere pressure [mbar]
    upward flux [W / m2]
    downward flux [W / m2]
    net flux [W / m2]
    heating rate [deg / day]
    signed_fluxes --- False for all positive valued fluxes
    True for downward fluxes to be negative and upward fluxes to be positive
    cooling_rate --- add a DataArray for cooling rate to the output Dataset
    OUTPUT:
    ds --- Xray Dataset,
    with dimensions:
    ib --- spectral band
    ik --- g-point
    pressure --- pressure at levels (interfaces)
    layer_pressure --- pressure at layers (levels)
    with data variables:
    flux_up --- upward flux
    flux_down --- downward flux
    net_flux --- net flux
    heating_rate --- heating rate
    [cooling_rate] --- cooling rate
    '''
    df = pd.read_csv(fpath, sep = r'\s+', skiprows = [0], header = None,
                     names = ['ib', 'ik', 'k', \
                              'pressure', 'flux_up', 'flux_down', 'net_flux', 'heating_rate'])
    
    df.drop(axis = 1, labels = ['k'], inplace = True) # drop level indices to avoid creating extra dimension
    df.set_index(['ib', 'ik', 'pressure'], inplace = True)
    
    ds = xray.Dataset.from_dataframe(df)
    
    layer_pressure_values = .5 * (ds.coords['pressure'][: -1].values + ds.coords['pressure'][1:].values)
    ds.coords['layer_pressure'] = layer_pressure_values
    
    da_heating_rates = ds['heating_rate'].sel(pressure = ds.coords['pressure'][1:])
    ds['heating_rate'] = (['ib', 'ik', 'layer_pressure'], da_heating_rates)
    
    if cooling_rate:
        ds['cooling_rate'] = - ds['heating_rate']
        
    if signed_fluxes:
        ds['flux_up'] *= -1
        ds['net_flux'] = ds['flux_up'] + ds['flux_down']
        
    return ds
