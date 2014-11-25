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
