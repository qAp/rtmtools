import os
import itertools
import collections
import sys
import numpy as np
import pandas as pd
import io

import rtmtools.lblrtm.aerutils as aerutils
import rtmtools.lblrtm.create_LBLRTM_input as lblrtmin







def lbl_run_input_params(path_lblf = 'lbl.f',
                         path_lbl_chouf90 = 'lbl_chou.f90',
                         in_the_form = 'dict'):
    '''
    Grab input parameters from an lbl run (from its source code:
    lbl.f and lbl_chou.f90)
    INPUT:
    path_lblf --- path to lbl.f
    path_lbl_chouf90 --- path to lbl_chou.f90
    '''
    params_deque = collections.deque([])

    # get parameters from lbl.f
    with open(path_lblf, mode = 'r', encoding = 'utf-8') as file:
        lblflines = file.read().split('\n')

    lines_assign = [line for line in lblflines if '=' in line]

    # get the line 'parameter(nlayer=75,vstar=0.,...)'
    paramsline = [line for line in lines_assign
                  if line.strip().startswith('parameter(nlayer')][0]
    params = paramsline.split('(')[-1].split(')')[0].split(',')
    params_deque.extend([param.split('=') for param in params])

    paramslines = [line.strip() for line in lines_assign\
                  if line.strip().startswith(('tsfc',
                                              'clayer',
                                              'qlayer',
                                              'rlayer'))]

    params = [line.split('=') for line in paramslines]
    params_deque.extend(params)

    # get parameters from lbl_chou.f90
    with open(path_lbl_chouf90, mode = 'r', encoding = 'utf-8') as file:
        chouflines = file.read().split('\n')

    dataline, valueline = [(line, chouflines[i + 1])\
                              for i, line in enumerate(chouflines)\
                              if all(wd in line for wd in ['data', 'flgh2o'])][0]
    flagnames = dataline.split('data')[-1].strip().split(',')
    flagvalues = [int(value.strip()) \
                     for value in valueline.split('/')[1].split(',')]
    params_deque.extend(zip(flagnames, flagvalues))
    return collections.OrderedDict(params_deque)

    




def sum_OUTPUT_RADSUM_over_wbands(pnl, V1 = 820., V2 = 50000.,
                                  names = ['flux_up', 'flux_down',
                                           'net_flux', 'heating_rate']):
    '''
    Sum fluxes and/or rates (heating or cooling) over wavenumbers
    INPUT:
    pnl --- Pandas Panel: ((V1, V2), atm level, [pressure, flux up, ..., rate])
    names --- attributes to sum up over wavenumbers
    V1, V2 --- lower and upper wavenumber limits in the sum
    OUTPUT:
    df --- Pandas DataFrame: (atm level, NAMES)
    '''
    V1s, V2s = (lev.values for lev in pnl.items.levels)
    item1, item2 = (np.abs(vs - v).argmin() 
                    for vs, v in zip([V1s, V2s], [V1, V2]))
    print('item1', item1, 'item2', item2)
    print('v1', pnl.items[item1], 'v2', pnl.items[item2])
    pnldata = pnl.values
    dfdata = pnldata[item1 : item2 + 1, :, 1:].sum(axis = 0)
    df = pd.DataFrame(dfdata, columns = names, index = pnl.major_axis)
    return pd.concat([pnl.ix[pnl.items[0], :, 'pressure'], df], axis = 1)

    
# the following doesnt work!!    
#    return pd.concat([pnl.ix[pnl.items[0], :, 'pressure'],
#                      pnl.ix[item1: item2 + 1, :, names].sum(axis = 'items')],
#                     axis = 1)






def save_OUTPUT_RADSUM_summary(path_OUTPUT_RADSUM = '',
                               path_atmpro = '',
                               saveas = 'test.xlsx',
                               wavenumber_bands = [(0., 3000.)],
                               atmpro_data_names = ['plevel', 'tlayer',
                                                    'wlayer', 'olayer']):
    
    '''
    Summarises and writes results of a line-by-line calculation to
    an Excel file
    '''
    # wave number bands
    band_labels = ['{} ~ {} cm-1'.format(v1, v2) for v1, v2 in wavenumber_bands]

    # sum fluxes and cooling rates over wavenumbers in each of the specified 
    # wavenumber bands
    outrads = [aerutils.sum_OUTPUT_RADSUM_over_wave_numbers(
        readfrom = path_OUTPUT_RADSUM, V1 = v1, V2 = v2)
               for v1, v2 in wavenumber_bands]

    # get top-tropopause-surface fluxes summary
    trilevs = [70, 37, 0]
    outrads_trilevs = [pd.DataFrame(outrad.ix[trilevs, 1: -1].values,
                                    index = outrad.ix[trilevs, 'pressure'],
                                    columns = outrad.columns[1: -1])
                       for outrad in outrads]
    three_levels_summary = pd.concat(outrads_trilevs, axis = 0,
                                     keys = band_labels,
                                     names = ['wavenumber band', 'pressure'])

    # get cooling rate for the whole of this line-by-line calculation's 
    # wavenumber range
    outrad = aerutils.sum_OUTPUT_RADSUM_over_wave_numbers(
        readfrom = path_OUTPUT_RADSUM,
        V1 = wavenumber_bands[0][0], V2 = wavenumber_bands[-1][-1])
    cor_df = pd.DataFrame(
        {'pressure': .5 * (outrad.values[: -1, 0] + outrad.values[1:, 0]),
         'cooling_rate': outrad.values[1:, -1]})
    cor_df.index = range(cor_df.shape[0])[::-1]
    cor_df = cor_df.loc[:, ['pressure', 'cooling_rate']]



    if path_atmpro.endswith('.pro'):
        atmpro = aerutils.atmpro_PROfile_to_pandasDataFrames(
            readfrom = path_atmpro,
            data_names = atmpro_data_names)
    else:
        atmpro = aerutils.atmpro_txtfile_to_pandasDataFrame(
            readfrom = path_atmpro)
        
    if saveas.endswith('.xlsx'):
        with pd.ExcelWriter(saveas) as writer:
            atmpro.to_excel(writer, sheet_name = 'atm profile')
            [outrad.to_excel(writer, sheet_name = label)
             for label, outrad in zip(band_labels, outrads)]
            cor_df.to_excel(writer, sheet_name = 'cor plotdata')
            three_levels_summary.to_excel(writer,
                                          sheet_name = '3 levels summary')
    else:
        waveband_keys = ['V1_{}_V2_{}'.format(v1, v2) for v1, v2 in wavenumber_bands]
        with pd.get_store(saveas, mode = 'w') as store:
            store.append('atmpro', atmpro)
            [store.append('/'.join(['wavebands', label]), outrad)
             for label, outrad in zip(waveband_keys, outrads)]
            store.append('cor_plotdata', cor_df)
            store.append('three_levels', three_levels_summary)



            

def lines2bands(pnl, wbands = None):
    '''
    Group fine wavenumber intervals into bands
    INPUT:
    pnl --- Pandas Panel
            (wavenumber, level, [pressure, flux, ..., heating rate])
    wbands --- wavenumber bands. a list of tuples.
    '''
    return pd.Panel({(V1, V2):
                     sum_OUTPUT_RADSUM_over_wbands(pnl, V1 = V1, V2 = V2)
                     for V1, V2 in wbands}) 


def normalise_by_TOA_flux_down(pnl, normalise_to = None):
    '''
    Normalise top-of-atmosphere downward flux of PNL
    to a specified value.
    INPUT:
    pnl --- flux to be normalised (Pandas Panel)
    normalise_to --- if a scalar value, the value to normalise to
                     if another Pandas Panel, normalise to its
                     top-of-atmosphere downward flux
    '''
    names = ['flux_up', 'flux_down', 'net_flux']
    for item in pnl.items:
        df1, df2 = pnl[item], normalise_to[item]
        df1.loc[:, names] *= (
            df2.loc[df1.index[0], 'flux_down'] /
            df1.loc[df1.index[0], 'flux_down'])
    return pnl
            

        






