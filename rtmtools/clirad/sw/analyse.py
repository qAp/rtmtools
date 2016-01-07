import os
import sys
import itertools
import collections
import io

import numpy as np
import pandas as pd

import rtmtools.lblrtm.aerutils as aerutils
import rtmtools.lblrtm.aeranalyse as aeranalyse
import rtmtools.clirad.sw.info


def sum_OUTPUT_CLIRAD_over_wbands(pnl, wbands = range(1, 9)):
    return pd.concat([pnl.ix[1, :, 'pressure'],
                      pnl.ix[wbands, :, 1:].sum(axis = 'items')],
                     axis = 1)



def lines2bands(pnl, wbands = None):
    '''
    Cast PNL into wbands which might not be continuous,
    monotonic, and non-overlapping, like CLIRAD-SW\'s wavenumber bands
    INPUT:
    wbands -- dictionary of {id: [(V1, V2), ...]}, where ID is a unique
              label for a wavenumber band, and [(V1, V2), ...] is a list
              of one or more wavenumber ranges in the wavenumber band, and
              V1 and V2 are the lower and upper wavenumbers of each range,
              respectively  
    '''
    dict_pnlout = {}
    for id, wranges in wbands.items():
        V1s, V2s = zip(*wranges)
        pnl_id = aeranalyse.lines2bands(pnl, wbands = wranges)
        df_id = aeranalyse.sum_OUTPUT_RADSUM_over_wbands(pnl_id,
                                                         V1 = min(V1s), V2 = max(V2s))
        dict_pnlout[id] = df_id
    return pd.Panel(dict_pnlout)


def hr_from_pnl_clirad(pnl_clirad, ib=6):
    '''
    Returns heating rate in a CLIRAD-SW spectral band from a CLIRAD-SW calculation.
    INPUT:
    pnl_clirad --- Pandas.Panel loaded from OUTPUT_CLIRAD
    ib --- which spectral band
    OUTPUT:
    hr --- Pandas.Series containing heating rate for spectral band ib
    '''
    df = sum_OUTPUT_CLIRAD_over_wbands(pnl_clirad, wbands=[ib])
    hr = df['heating_rate'][1:]

    layer_pressure = .5 * (df['pressure'][:-1].values + df['pressure'][1:].values)
    hr.index = layer_pressure

    return hr


def hr_from_pnl_crd(pnl_crd, ib=6):
    '''
    Returns heating rate in a CLIRAD-SW spectral band from a CRD-SW calculation.
    INPUT:
    pnl_crd --- Pandas.Panel loaded from OUTPUT_RADSUM
    ib --- which spectral band
    OUTPUT:
    hr --- Pandas.Series containing heating rate for spectral ib
    '''
    bands_cliradsw = rtmtools.clirad.sw.info.wavenumber_bands()
    pnl_crd_bands = lines2bands(pnl_crd, wbands=bands_cliradsw)
    df = pnl_crd_bands[ib]
    
    hr = df['heating_rate'][1:]
    layer_pressure = .5 * (df['pressure'][:-1].values + df['pressure'][1:].values)
    hr.index = layer_pressure
    
    return hr
