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
    

    
