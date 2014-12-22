import os
import sys
import itertools
import collections
import io

import numpy as np
import pandas as pd



def sum_OUTPUT_CLIRAD_over_wbands(pnl, \
                                  names = ['flux_up', 'flux_down', 'net_flux',\
                                           'heating_rate'], \
                                  wbands = range(1, 9)):
    return pd.concat([pnl.ix[1, :, 'pressure'],
                      pnl.ix[wbands, :, names].sum(axis = 'items')],
                     axis = 1)
