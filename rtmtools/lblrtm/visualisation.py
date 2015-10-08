import os
import io
import itertools
import collections
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt




def tabulate_difference(dfs, names = None, title = None,
                        difference_only = False):
    '''
    Prints out the difference between all pairs of Data Frames
    in DFS.  Set DIFFERENCE_ONLY to TRUE to not to print out
    values of each Data Frame in DFS.
    INPUT:
    names --- list of strings, names for each Data Frame in DFS
    title --- string to be written at the very top
    '''
    df_pairs = itertools.combinations(zip(names, dfs), 2)

    print()
    print(title)
    
    if not difference_only:
        for name, df in zip(names, dfs):
            print()
            print('{}'.format(name))
            print(df)
    
    for (name1, df1), (name2, df2) in df_pairs:
        print()
        print('{} - {}'.format(name1, name2))
        print(df1 - df2)

    print()


def plot_pres_vs_flux_down(dfs,
                           names = None, linestyles = None, colours = None,
                           title = None,
                           pres_scale = 'linear'):
    '''
    Plot pressure versus flux down for one or more Data Frames
    '''
    pressures = [df['pressure'].values for df in dfs]
    flux_downs = [df['flux_down'].values for df in dfs]

    xys = zip(flux_downs, pressures)
    xys = itertools.chain(*xys)

    matplotlib.rcParams.update({'font.size': 20})
    fig = plt.figure(figsize = (8, 8))
    ax = fig.add_subplot(111,
                         title = title if title else '',
                         xlabel = 'flux [$W m^{-2}$]',
                         ylabel = 'pressure [mb]')
    lines = ax.plot(*xys)

    [plt.setp(line, linestyle = style, color = colour, linewidth = 2)\
     for line, style, colour in zip(lines, linestyles, colours)]
    ax.set_yscale(pres_scale)
    ax.xaxis.get_major_formatter().set_powerlimits((0, 1))
    plt.grid(b = True)
    plt.legend(names, loc = 'best')
    plt.gca().invert_yaxis()



def plot_pres_vs_hrcr(dfs,
                      names = None, linestyles = None, colours = None,
                      title = None,
                      cooling_rate = False,
                      pres_scale = 'linear'):
    '''
    Plot pressure versus rate of either heating or cooling
    given for Data Frames
    '''
    rate_label = 'cooling_rate' if cooling_rate else 'heating_rate'
    pressures = [.5 * (df['pressure'].values[: -1] +
                       df['pressure'].values[1: ]) for df in dfs]
    rates = [df[rate_label].values[1:] for df in dfs]
    xys = list(itertools.chain(*zip(rates, pressures)))

    matplotlib.rcParams.update({'font.size': 15})
    fig = plt.figure(figsize = (15, 8))
    
    ax = fig.add_subplot(121,
                         xlabel = '{} [deg/day]'.format(rate_label),
                         ylabel = 'pressure [mb]')
    lines = ax.plot(*xys)

    [plt.setp(line, linestyle = style, color = colour, linewidth = 2.)\
     for line, style, colour in zip(lines, linestyles, colours)]

    ax.xaxis.get_major_formatter().set_powerlimits((0, 1))
    ax.grid(b = True)
    ax.legend(names, loc = 'best')
    ax.invert_yaxis()
    ax.set_yscale('linear')

    axlog = fig.add_subplot(122,
                            xlabel = '{} [deg/day]'.format(rate_label),
                            ylabel = 'pressure [mb]')
    lines = axlog.plot(*xys)
    [plt.setp(line, linestyle = style, color = colour, linewidth = 2.)\
     for line, style, colour in zip(lines, linestyles, colours)]
    axlog.xaxis.get_major_formatter().set_powerlimits((0, 1))
    axlog.grid(b = True)
    axlog.legend(names, loc = 'best')
    axlog.invert_yaxis()
    axlog.set_yscale('log')

    fig.suptitle(title if title else '', fontsize = 15)

    
