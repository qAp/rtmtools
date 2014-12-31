import os
import collections
import itertools
import io
import numpy as np
import pandas as pd








def sum_OUTPUT_RRTM_over_wbands(pnl,
                                names = ['flux_up', 'flux_down', 'net_flux',
                                         'heating_rate'],
                                V1 = 820., V2 = 50000.):
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
    print(item1, item2)
    return pd.concat([pnl.ix[pnl.items[0], :, 'pressure'],
                      pnl.ix[item1: item2 + 1, :, names].sum(axis = 'items')],
                     axis = 1)
