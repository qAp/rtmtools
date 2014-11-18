import matplotlib
matplotlib.use('Agg')
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import itertools
import collections
import rtmtools.lblrtm.aerutils as aerutils
import lblutils


def atmpro_simpleplot(atmpro_dict, property = 'temperature',
                      against = 'pressure'):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(atmpro_dict[against]['data'], atmpro_dict[property]['data'])
    ax.set_ylabel('{name} [{units}]'.format(**atmpro_dict[property]))
    ax.set_xlabel('{name} [{units}]'.format(**atmpro_dict[against]))
    ax.set_title('{name}'.format(**atmpro_dict[property]))
    return fig



def atmpro_conventionalplot(atmpro_dict, property = 'temperature',
                             against = 'pressure'):
    '''
    This plots in the style that has been seen for cooling rates.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.semilogy(atmpro_dict[property]['data'],
                atmpro_dict[against]['data'])
    plt.gca().invert_yaxis()
    ax.set_ylabel('{name} [{units}]'.format(**atmpro_dict[against]))
    ax.set_xlabel('{name} [{units}]'.format(**atmpro_dict[property]))
    ax.set_title('{name}'.format(**atmpro_dict[property]))
    return fig
    

def atmpro_from_txtfile(filepath = 'atmopro.dat', fmt = 'png',
                        savein = 'figs_atmpro', return_figs = False,
                        plot_style = 'conventional'):
    '''
    Plots the atmospheric profile in FILEPATH, save in
    format FMT and save in a directory called SAVEIN.
    '''
    if plot_style is 'simple':
        plot_func = atmpro_simpleplot
    elif plot_style is 'conventional':
        plot_func = atmpro_conventionalplot
    else:
        plot_func = atmpro_conventionalplot
    
    properties = ('altitude', 'temperature',
                  'H2O', 'CO2', 'O3', 'N2O', 'CO', 'CH4', 'O2')
    atmpro_dict = aerutils.read_atmpro_txtfile(filepath)

    figures = [plot_func(atmpro_dict, property = property)
               for property in properties]
    
    aerutils.save_figures_by_property(figures, properties, savein, fmt)
    
    if return_figs:
        return figures
    else:
        plt.close('all')


def output_fluxcalc(filepath = 'OUTPUT_RADSUM', fmt = 'png',
                    savein = 'figs_flux', return_figs = False,
                    heating_rate_only = True,
                    plot_style = 'conventional', cooling_rate = True
                    ):
    '''
    Plots the results of flux calculations in FILEPATH, save in format
    FMT and in directory SAVEIN

    Notes:
          plot_style = \'conventional\' uses a loglog plot, so values have
          to be positive.
    '''
    if plot_style is 'simple':
        plot_func = atmpro_simpleplot
    elif plot_style is 'conventional':
        plot_func = atmpro_conventionalplot
    else:
        plot_func = atmpro_conventionalplot
        
    properties = ('heating_rate', 'flux_up', 'flux_down', 'net_flux')
    radsum = aerutils.read_OUTPUT_RADSUM(filepath)

    if cooling_rate:
        property = 'cooling_rate'
        radsum['cooling_rate'] = {'data': - radsum['heating_rate']['data'],
                                  'name': 'cooling_rate',
                                  'units': radsum['heating_rate']['units']}
    else:
        property = 'heating_rate'
        
    figures = [plot_func(radsum, property = property,
                                 against = 'pressure')]
    if not heating_rate_only:
        figures.extend(atmpro_simpleplot(radsum, property = property,
                                         against = 'pressure')
                    for property in properties[1:])

    aerutils.save_figures_by_property(figures, properties, savein, fmt)
    
    if return_figs:
        return figures
    else:
        plt.close('all')


    


def cooling_rate_lbl_and_lblrtm(lblpath = '/nuwa_cluster/home/jackyu/line_by_line/lbl/runs/lbl_H2012_h20_cut10/H2012_h2o_IR_cor_dv002.dat',
                                aerpath = '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/radsum/run_mls75pro_uptolev59_H2O/OUTPUT_RADSUM',
                                fmt = 'png', savein = 'figs_lbl_lblrtm/', return_figs = False):
    '''
    Plots cooling rate from lbl and lblrtm
    '''
    property = 'cooling_rate'
    dict_lbl = lblutils.read_cooling_rate_txtfile(lblpath)
    dict_aer = aerutils.read_OUTPUT_RADSUM(aerpath)

    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.semilogy(dict_lbl['cooling_rate']['data'], dict_lbl['pressure']['data'],
                - dict_aer['heating_rate']['data'], dict_aer['pressure']['data'])
    plt.legend(('lbl', 'lblrtm'), loc = 'best')
    plt.gca().invert_yaxis()
    ax.set_ylabel('pressure [mb]')
    ax.set_xlabel('cooling_rate [deg/day]')
    ax.set_title('cooling_rate')
    
    aerutils.save_figures_by_property((figure, ), (property, ), savein, fmt)

    if return_figs:
        return figures
    else:
        plt.close('all')



def cooling_rate_from_txtfiles(readfrom = ['OUTPUT_RADSUM'],
                               legends = ['AER'],
                               saveas = 'figs_coolingrate/coolingrate.png',
                               return_figs = False,
                               plot_style = 'conventional',
                               xlim = [-3, 3],
                               ylim = [1e-3, 1e3]):
    
    '''
    Plot cooling rates from a list of LBLRTM-produced OUTPUT_RADSUM, or lbl-produced .dat files
    '''
    ds = (
        lblutils.read_cooling_rate_txtfile(file) if file.endswith('.dat') and '_cor' in file
        else aerutils.OUTPUT_RADSUM_to_pandasPanel(readfrom = file, cooling_rate = True)
    for file in readfrom
    )
    
    pcs = (
    (d['cooling_rate']['data'], d['pressure']['data']) if file.endswith('.dat') and '_cor' in file
    else (np.sum(d.values[:, 1:, -1], axis = 0), .5 * (d.values[0, :-1, 0] + d.values[0, 1:, 0])) 
    for file, d in zip(readfrom, ds)
    )

    figure = plt.figure()
    ax = figure.add_subplot(111)
    if plot_style is 'linear':
        ax.plot(*itertools.chain(*pcs))
    else:
        ax.semilogy(*itertools.chain(*pcs))
    plt.legend(legends, loc = 'best')
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    ax.set_ylabel('pressure [mb]')
    ax.set_xlabel('cooling_rate [deg/day]')
    ax.set_title('cooling_rate')
    plt.gca().invert_yaxis()

    try:
        property, fmt = os.path.basename(saveas).split('.')
    except ValueError:
        property, fmt = os.path.basename(saveas), ''
        
    aerutils.save_figures_by_property((figure, ), (property, ), os.path.dirname(saveas), fmt)

    if return_figs:
        return figure
    else:
        plt.close('all')


if __name__ == '__main__':
    pass
