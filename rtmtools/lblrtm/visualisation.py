import os
import io
import itertools
import collections
import sys
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt




def tabulate_difference(df1, df2, names = ['df1', 'df2'], title = None):
    '''
    Prints out the results of DF2 subtracted from DF1
    '''
    print()
    print(title)
    print(names[0])
    print(df1)
    print(names[1])
    print(df2)
    print('{} - {}'.format(*names))
    print(df1 - df2)
    print()


def plot_pres_vs_flux_down(dfs,
                           names = None, linestyles = None, colours = None,
                           title = None):
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
    ax.set_yscale('linear')
    ax.xaxis.get_major_formatter().set_powerlimits((0, 1))
    plt.grid(b = True)
    plt.legend(names, loc = 'best')
    plt.gca().invert_yaxis()



def plot_pres_vs_hrcr(dfs,
                      names = None, linestyles = None, colours = None,
                      title = None,
                      cooling_rate = False):
    '''
    Plot pressure versus rate of either heating or cooling
    given for Data Frames
    '''
    rate_label = 'cooling_rate' if cooling_rate else 'heating_rate'
    pressures = [.5 * (df['pressure'].values[: -1] +
                       df['pressure'].values[1: ]) for df in dfs]
    rates = [df[rate_label].values[1:] for df in dfs]
    xys = itertools.chain(*zip(rates, pressures))

    matplotlib.rcParams.update({'font.size': 20})
    fig = plt.figure(figsize = (8, 8))
    ax = fig.add_subplot(111,
                         title = title if title else '',
                         xlabel = '{} [deg/day]'.format(rate_label),
                         ylabel = 'pressure [mb]')
    lines = ax.plot(*xys)

    [plt.setp(line, linestyle = style, color = colour, linewidth = 2.)\
     for line, style, colour in zip(lines, linestyles, colours)]
    ax.set_yscale('log')
    ax.xaxis.get_major_formatter().set_powerlimits((0, 1))
    plt.grid(b = True)
    plt.legend(names, loc = 'best')
    plt.gca().invert_yaxis()
