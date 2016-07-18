import os
import io
import itertools
import collections
import sys
import random
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D



def matplotlib_basic_colours():
    '''
    Returns a list of plot colours available in matplotlib.
    The colours in this list are easily distinguished from each
    other by eye.
    '''
    return ['b', 'g', 'r', 'c', 'm', 'y', 'k']



def matplotlib_nonnothing_linestyles(longname = False):
    '''
    Returns the list of plot linestyles available in matplotlib.
    Linestyles that are invisible are left out of this list.
    '''
    if longname:
        return [v for k, v in Line2D.markers.items() if v != '_draw_nothing']
    else:
        return [k for k, v in Line2D.lineStyles.items() if v != '_draw_nothing']
    
    
    
def matplotlib_nonnothing_markers(longname = False):
    '''
    Returns the list of plot markers available in matplotlib.
    Markers that are invisible are left out of this list.
    '''
    if longname:
        return [v for k, v in Line2D.markers.items() if v != 'nothing']
    else:
        return [k for k, v in Line2D.markers.items() if v != 'nothing']
    


def matplotlib_colour_linestyle_tuples(N = 10):
    '''
    Returns a shuffled list of unique tuples of plot colours and linestyles
    of length Npairs.
    INPUT:
    Npairs --- length of list returned,
    the number of unique tuples of plot colours and linestyles returned.
    '''
    colours = matplotlib_basic_colours()
    linestyles = matplotlib_nonnothing_linestyles()
    
    uniques = list(itertools.product(colours, linestyles))
    
    random.shuffle(uniques)
    return random.sample(uniques, N)




def matplotlib_colour_linestyle_marker_tuples(N = 10):
    colours = matplotlib_basic_colours()
    linestyles = matplotlib_nonnothing_linestyles()
    markers = matplotlib_nonnothing_markers()
    
    uniques = list(itertools.product(colours, linestyles, markers))
    
    random.shuffle(uniques)
    return random.sample(uniques, N)


def tabulate_difference(dfs, names=None, title=None,
                        return_original=True):
    '''
    For a list of dataframes, calculate the difference
    between all possible pairs.

    Parameters
    ----------
    dfs: list of pandas.DataFrame
    names: list of names corresponding to `dfs`
    return_original: True to return dataframes in dfs, else False
    df_all: pandas.DataFrame containing dataframes of differences
            and maybe the original dataframes too if `return_original`
            is True
    '''
    df_pairs = itertools.combinations(zip(names, dfs), 2)

    results = [('{} - {}'.format(name1, name2),
                df1 - df2)
               for (name1, df1), (name2, df2) in df_pairs]

    names_diff, dfs_diff = zip(*results)

    if return_original:
        names_all = names + list(names_diff)
        dfs_all = dfs + list(dfs_diff)
    else:
        names_all = names_diff
        dfs_all = dfs_diff
        
    df_all = pd.concat(dfs_all, keys=names_all)
    return df_all
        

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
