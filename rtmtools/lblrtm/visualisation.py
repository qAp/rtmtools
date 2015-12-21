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
                      xlim_linear = None, xlim_log = None,
                      ylim = None):
    '''
    Plot pressure versus rate of either heating or cooling
    given for Data Frames
    '''
    rate_label = 'cooling_rate' if cooling_rate else 'heating_rate'
    pressures = [.5 * (df['pressure'].values[: -1] +
                       df['pressure'].values[1: ]) for df in dfs]
    rates = [df[rate_label].values[1:] for df in dfs]

    dfs_rates = [pd.Series(df[rate_label].values[1:],
                             index = .5 * (df['pressure'].values[: -1] \
                                           + df['pressure'].values[1: ]))
                for df in dfs]

    xys = list(itertools.chain(*[(df_rates.values, df_rates.index.values) \
                                 for df_rates in dfs_rates]))

    matplotlib.rcParams.update({'font.size': 15})
    fig = plt.figure(figsize = (15, 8))
    
    ax = fig.add_subplot(121,
                         xlabel = '{} [deg/day]'.format(rate_label),
                         ylabel = 'pressure [mb]')
    
    lines = ax.plot(*xys)

    [plt.setp(line, linestyle = style, color = colour, linewidth = 2.)\
     for line, style, colour in zip(lines, linestyles, colours)]

    ax.grid(b = True)
    ax.legend(names, loc = 'best')

    ax.xaxis.get_major_formatter().set_powerlimits((0, 1))
    if xlim_linear:
        ax.set_xlim(xlim_linear)
    else:
        if ylim:
            ymin, ymax = ylim
            xmin = min([df[(df.index > 1e0) & (df.index < ymax)].min() for df in dfs_rates])
            xmax = max([df[(df.index > 1e0) & (df.index < ymax)].max() for df in dfs_rates])
        else:
            xmin = min([df[df.index > 1e0].min() for df in dfs_rates])
            xmax = max([df[df.index > 1e0].max() for df in dfs_rates])
        dx = xmax - xmin
        xmin -= .1 * dx
        xmax += .1 * dx
        ax.set_xlim((xmin, xmax))

    if ylim:
        ax.set_ylim(ylim)
    ax.set_yscale('linear')
    ax.invert_yaxis()


    axlog = fig.add_subplot(122,
                            xlabel = '{} [deg/day]'.format(rate_label),
                            ylabel = 'pressure [mb]')
    
    lines_log = axlog.plot(*xys)
    
    [plt.setp(line, linestyle = style, color = colour, linewidth = 2.)\
     for line, style, colour in zip(lines_log, linestyles, colours)]

    axlog.grid(b = True)
    axlog.legend(names, loc = 'best')
        
    axlog.xaxis.get_major_formatter().set_powerlimits((0, 1))
    if xlim_log:
        axlog.set_xlim(xlim_log)
    else:
        if ylim:
            ymin, ymax = ylim
            xmin = min([df[(df.index < 1e0) & (df.index > ymin)].min() for df in dfs_rates])
            xmax = max([df[(df.index < 1e0) & (df.index > ymin)].max() for df in dfs_rates])
        else:
            xmin = min([df[df.index < 1e0].min() for df in dfs_rates])
            xmax = max([df[df.index < 1e0].max() for df in dfs_rates])
        dx = xmax - xmin
        xmin -= .1 * dx
        xmax += .1 * dx
        axlog.set_xlim((xmin, xmax))

    if ylim:
        axlog.set_ylim(ylim)    
    axlog.set_yscale('log')
    axlog.invert_yaxis()


    fig.suptitle(title if title else '', fontsize = 15)

    


def plot_pdseries_indexVSvalues_linearlog(srss = None,
                                          names = None,
                                          colours = None, linestyles = None, markers = None,
                                          ylim = None,
                                          xlim_linear = None, xlim_log = None,
                                          title = None, ylabel = None, xlabel = None,
                                          figsize = (8, 5)):
    '''
    Plots index versus values for one or more Pandas.Series,
    for both linear and log y-scales.
    
    When y-scale is linear, x-axis limits are the minimum and maximum
    values for the range of y above 1.  When y-scale log, x-axis limits
    are the minumum and maximum values for the range of y below 1.
    
    INPUT:
    srss --- list of Pandas series to plot
    names --- corresponding list of strings to label the above; these are used in the legend
    colours --- corresponding list of matplotlib colours (e.g. \'k\', \'r\', etc.)
    linestyles --- corresponding list of matplotlib linestyles (e.g. \'-\', \'--\', etc.)
    markers --- corresponding list of matplotlib markers (e.g. \'o\', \'+\', etc.)
    ylim --- a tuple of length two containing the lower and upper limits on the y-axis
    xlim_linear --- a tuple of length two containing the lower and upper limits on the linear x-axis
    xlim_log --- a tuple of length two containing the lower and upper limits on the log x-axis
    title --- string containing the title of the figure
    xlabel --- string containing the x-axis label
    ylabel --- string containing the y-axis label
    figsize --- tuple of length two containing the width and height, in centimetres, of the figure
    OUTPUT:
    fig --- matplotlib figure object for the plot
    '''
    xys = list(itertools.chain(*[(srs.values, srs.index.values) for srs in srss]))
    
    if not markers:
        markers = [None for _ in range(len(xys))]
        
    if not linestyles:
        linestyles = ['None' for _ in range(len(xys))]
        
    fig, axs = plt.subplots(nrows = 1, ncols = 2, figsize = figsize)
    
    for yscale, ax in zip(('linear', 'log'), axs):
        
        lines = ax.plot(*xys)
        
        [plt.setp(line, \
                  linestyle = style, color = colour, marker = marker,\
                  linewidth = 2.)\
         for line, style, colour, marker in zip(lines, linestyles, colours, markers)]
        
        ax.set_title(title)
        ax.grid(b = True)
        ax.legend(names, loc = 'best')

        if ylim:
            ax.set_ylim(ylim)
        ax.set_yscale(yscale)
        ax.invert_yaxis()
        ax.set_ylabel(ylabel)
        
        if yscale == 'linear':
            if xlim_linear:
                ax.set_xlim(xlim_linear)
            else:
                if ylim:
                    ymin, ymax = ylim
                    xmin = min([srs[(srs.index > 1e0) & (srs.index < ymax)].min() for srs in srss])
                    xmax = max([srs[(srs.index > 1e0) & (srs.index < ymin)].max() for srs in srss])
                else:
                    xmin = min([srs[srs.index > 1e0].min() for srs in srss])
                    xmax = max([srs[srs.index > 1e0].max() for srs in srss])
                    
                dx = xmax - xmin
                xmin -= .1 * dx
                xmax += .1 * dx
                ax.set_xlim((xmin, xmax))
        elif yscale == 'log':
            if xlim_log:
                ax.set_xlim(xlim_log)
            else:
                if ylim:
                    ymin, ymax = ylim
                    xmin = min([srs[(srs.index < 1e0) & (srs.index > ymin)].min() for srs in srss])
                    xmax = max([srs[(srs.index < 1e0) & (srs.index > ymin)].max() for srs in srss])
                else:
                    xmin = min([srs[srs.index < 1e0].min() for srs in srss])
                    xmax = max([srs[srs.index < 1e0].max() for srs in srss])
                    
                dx = xmax - xmin
                xmin -= .1 * dx
                xmax += .1 * dx
                ax.set_xlim((xmin, xmax))
                
        ax.xaxis.get_major_formatter().set_powerlimits((0, 1))
        ax.set_xlabel(xlabel)
    return fig
