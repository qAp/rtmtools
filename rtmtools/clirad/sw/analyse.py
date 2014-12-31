import os
import sys
import itertools
import collections
import io

import numpy as np
import pandas as pd

import rtmtools.lblrtm.aerutils as aerutils
import rtmtools.lblrtm.aeranalyse as aeranalyse



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
    
