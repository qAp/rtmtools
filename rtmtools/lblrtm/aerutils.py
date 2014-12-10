import os
import sys
import numpy as np
import itertools
import collections
import unicodedata
import pandas
import scipy.io as spio

dict_JCHARP = {'A': 'mb', 'B': 'atm', 'C': 'torr'}
dict_JCHART = {'A': 'K', 'B': 'C'}
dict_JCHAR = {'A': 'ppmv', 'B': 'cm-3', 'C': 'gm/kg', 'D': 'gm m-3',
              'E': 'mb',
              'F': 'dew point temp (K) *H2O only*',
              'G': 'dew point temp (C) *H2O only*',
              'H': 'relative humidity (percent) *H2O only*',
              'I': 'available for user identification'}
units_tags_dict = {'pressure': dict_JCHARP,
                   'temperature': dict_JCHART,
                   'molecule': dict_JCHAR}

def atmpro_units_tags_mapping():
    '''
    Tags for units of various atmospheric profile properties used in LBLRTM
    '''
    d = {}
    d['pressure'] = dict(zip((0, 1), zip(*dict_JCHARP.items())))
    d['temperature'] = dict(zip((0, 1), zip(*dict_JCHART.items())))
    d['molecule'] = dict(zip((0, 1), zip(*dict_JCHAR.items())))
    return d


def molecular_mass_mapping():
    substances = (('air', 28.97),
                  ('H2O', 18.016),
                  ('CO2', 44.),
                  ('O3', 48.),
                  ('N2O', 44.),
                  ('CO', 28.),
                  ('CH4', 16.),
                  ('O2', 32.))
    d = dict(substances)
    return lambda substance_name: d[substance_name]


def mixingratio_volume2mass(substance_name = 'H2O', volume_mix = .1):
    '''
    Convert volume mixing ratio to mass mixing ratio
    INPUT:
    substance_name --- name of substance
    volume_mix --- value of volume mixing ratio
    Note that the volume mixing ratio can be in different units,
    such as [ml/l], [ppmv], etc. 
    '''
    d = molecular_mass_mapping()
    return d(substance_name) * volume_mix / d('air')


def mixingratio_mass2volume(substance_name = 'H2O', mass_mix = .1):
    '''
    Convert mass mixing ratio to volume mixing ratio
    INPUT:
    substance_name --- name of substance
    mass_mix --- value of mass mixing ratio
    Note that the mass mixing ratio can be in different units,
    such as [g/g], [mg/g], [ppmm], etc.
    '''
    d = molecular_mass_mapping()
    return d('air') * mass_mix / d(substance_name)


def atmpro_units_tags_translate(property = 'pressure', units = 'mbar', unitsin = 'units'):
    '''
    Translate units between units and tags for atmospheric property PROPERTY.
    unitsin --- \'units\' or \'tags\'
    '''
    units_original = units
    units = (units_original, ) if isinstance(units_original, str) else units_original
    mapping = atmpro_units_tags_mapping()
    unitsin = 1 if unitsin is 'units' else 0
    samealreadys = (unit in mapping[property][unitsin] for unit in units)
    translator = dict(zip(mapping[property][1 - unitsin],
                          mapping[property][unitsin]))
    translated = tuple(translator[unit] if not samealready else unit
                       for samealready, unit in zip(samealreadys, units))
    return translated[0] if isinstance(units_original, str) else translated
    

    

def is_number(s):
    '''
    Checks if string S is a number
    http://www.pythoncentral.io/how-to-check-if-a-string-is-a-number-in-python-including-unicode/
    '''
    try:
        float(s)
        return True
    except ValueError:
        pass
    try:
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False


def insert_avgs(x, n = 0):
    '''
    Inserts into a numpy array between each pair the average of the pair
    INPUT:
    x --- numpy array into which to insert
    n --- number of iterations to insert
    '''
    if not x.shape[0] >= 2:
        raise ValueError('Inserting averages requires an array with at least 2 rows')
    if n == 0:
        return x
    elif n == 1:
        return np.insert(x, obj = range(1, x.shape[0]), values = .5 * (x[:-1] + x[1:]))
    else:
        return insert_avgs(insert_avgs(x, n - 1), 1)



def insert_levels_and_layers(xlevels,
                             between_levels = (1, 2), n = 0,
                             xlayerss = []):
    '''
    Insert extra levels between two levels, optionally repeatedly.
    If there are corresponding layers associated with the levels,
    also insert extra layers correspondingly.
    
    INPUT:
    xlevels --- numpy array representing values on levels
    between_levels --- tuple of length 2, representing the indices
                       of the levels between which extra levels/layers
                       are inserted (Note that the indices here
                       are the normal indices of lists/arrays,
                       and that the second index is inclusive)
    n --- number of iteration to insert
    xlayers --- list of numpy arrays each representing to values
                on layers corresponding to levels in xlevels
    '''
    if n == 0:
        return tuple(itertools.chain([xlevels], xlayerss))
    
    lev1, lev2 = between_levels
    
    if lev1 <= 0 or lev2 >= xlevels.shape[0] - 1:
        raise ValueError('It is not possible to insert layers\
        just inside the boundary levels, nor outside')
    
    xlevels_inserted = np.concatenate([xlevels[: lev1],
                                       insert_avgs(xlevels[lev1: lev2 + 1], n),
                                       xlevels[lev2 + 1:]], axis = 0)
    if not xlayerss:
        return (xlevels_inserted,)
    else:
        if not all([xlayers.shape[0] == xlevels.shape[0] - 1 for xlayers in xlayerss]):
            raise ValueError('All layer input arguments \
            must satisfy: Nlayers = Nlevels - 1')
        Xlayerss = [insert_avgs(xlayers[lev1 - 1: lev2 + 1], n = 1)[1: -1]
                    for xlayers in xlayerss]
        xlayers_inserted = [np.concatenate([xlayers[: lev1],
                                            insert_avgs(Xlayers, n = n)[1: -1: 2],
                                            xlayers[lev2:]],
                                           axis = 0)
                            for xlayers, Xlayers in itertools.zip_longest(xlayerss, Xlayerss)]
        return tuple(itertools.chain([xlevels_inserted], xlayers_inserted))




def atmpro_insert_levels_and_layers(atmpro,
                                    between_pressures = (.01, .1),
                                    n = 0):
    '''
    Insert levels and layers into atmosphere profile.
    INPUT:
    atmpro --- pandas data frame where the first column is level pressures
               and the rest are layer variables.
    between_pressures --- tuple of two pressures, lower and upper, between
                          which extra levels are to be inserted.
                          Units in mbars.
    n --- number of iterations of insertion
    '''
    p1, p2 = between_pressures
    if p2 < p1:
        raise ValueError('The second given pressure must be larger\
        than the first')

    # find numpy array indices of pressures closest to those specified
    index1 = atmpro.index.max() - (atmpro['plevel'] - p1).abs().argmin()
    index2 = atmpro.index.max() - (atmpro['plevel'] - p2).abs().argmin()

    if index2 == index1:
        raise ValueError('There is only one level in the pressure range\
        specified. Please specify a larger range, it needs to contain\
        at least 2 levels.')

    plevel = atmpro['plevel'].values
    xlayers = [atmpro[column].values[1:] for column in atmpro.columns
               if column != 'plevel']

    inserteds = insert_levels_and_layers(plevel, xlayerss = xlayers,
    between_levels = (index1, index2), n = n)

    inserted_series = [pandas.Series(inserted,
    index = range(inserted.shape[0])[::-1], name = column)
    for column, inserted in zip(atmpro.columns, inserteds)]

    return pandas.concat(inserted_series, axis = 1).sort_index(ascending = False)
        
    
    

def read_lblrtm_spectral_output_files(readfrom = 'TAPE13',
                                      max_lines = 1000):
    '''
    Returns a list of records from an unformatted Fortran file
    output by LBLRTM.  This is based on the IDL script
    read_lbl_file.pro which Karen provided.
    INPUT:
    readfrom --- path to the file to read
    max_lines --- maximum number of lines to read from file
    '''
    records = collections.deque([])
    f = spio.FortranFile(readfrom, mode = 'r')
    for k in range(max_lines):
        try:
            r = f.read_reals()
            records.append(r)
        except TypeError:
            print('Encountered TypeError on read_real().  \
            Stop reading and exit.')
            break
    f.close()
    return records





def read_atmpro_txtfile(filepath, translate_unit_tag = True):
    '''
    Returns a dictionary containing the atmospheric
    profile in FILEPATH
    '''
    properties = ('altitude', 'pressure', 'temperature',
                  'H2O', 'CO2', 'O3', 'N2O', 'CO', 'CH4', 'O2')

    with open(filepath, mode = 'r', encoding = 'utf-8') as forg:
        units = ['km'] + forg.readline().split()
        datas = np.array([[float(n) for n in line.split()]
                          for line in forg.read().split('\n') if line])

    if translate_unit_tag:
        units = [unit if property in ('altitude',)
                 else units_tags_dict[property][unit]
        if property in ('pressure', 'temperature')
        else units_tags_dict['molecule'][unit]
        for property, unit in itertools.zip_longest(properties, units)]

    return {property:
        {'name': property, 'units': unit, 'data': data}
        for property, unit, data in itertools.zip_longest(properties, units, datas.T)}





def atmpro_pandasDataFrames_to_PROfile(atmpro, saveas = 'default_name.pro',
                                       header = 'some atmospheric profile'):
    '''
    Write atmosphere profile in pandas data frame to formatted FORTRAN
    '''
    Nrow = 5
    
    name_and_values = [(column, atmpro[column].values)
                       if column == 'plevel'\
                       else (column, atmpro[column].values[1:])\
                       for column in atmpro.columns]
    
    lines_to_write = collections.deque([])
    for lbl_name, values in name_and_values:
        Nvalues = values.shape[0]

        if lbl_name == 'plevel':
            headline = '{:6}data ({:}(i),i=1,nlayer+1)/'
        else:
            headline = '{:6}data ({:}(i),i=1,nlayer)/'
        
        fmtrs = ('{:12.4e}' for _ in range(Nvalues))

        fmtrs = (
        ','.join(fmtr for fmtr in fmtr_group if fmtr)
        for fmtr_group in itertools.zip_longest(*(Nrow * [fmtrs]))
        )

        lines_to_write.extend(
        [headline.format('', lbl_name),
         ''.join(
            [',\n'.join((''.join(['{:5}&'.format(''), fmtr]) for fmtr in fmtrs)),
             '/\n', 'c']).format(*values)]
        )
    lines_to_write.appendleft('c{:5}{}'.format('', header))

    with open(saveas, mode = 'w', encoding = 'utf-8') as file:
        file.write('\n'.join(lines_to_write))    







def atmpro_PROfile_to_pandasDataFrames(readfrom = 'mls75.pro',
                                       data_names = ['plevel', 'tlayer', 'wlayer', 'olayer']):
    '''
    Reads atmosphere profile from a formatted FORTRAN file
    and returns a Pandas DataFrame. 
    '''
    with open(readfrom, mode = 'r', encoding = 'utf-8') as file:
        c = file.read()
        
    profiles = (
        np.array([float(n.rstrip(',/'))
                  for n in v.split()[1:]
                  if n.endswith(',') or n.endswith('/')])[::-1]
    for v in c.split('data')[1:]
    )

    profiles = (pandas.Series(profile,
                              index = range(profile.shape[0]),
                              name = name)
                for profile, name in zip(profiles, data_names))
    
    return pandas.concat(profiles, axis = 1).sort_index(ascending = False)
    
    
    


def atmpro_txtfile_to_pandasDataFrame(readfrom = 'mls75pro.dat'):
    '''
    Reads an atmosphere profile text file and returns the profile
    in a Pandas DataFrame, with highest presure at the bottom of the
    table.
    '''
    atmpro = pandas.read_csv(readfrom, header = None, skiprows = 1, sep = r'\s+')
    atmpro.columns = ['altitude', 'pressure', 'temperature',
                      'H2O', 'CO2', 'O3', 'N2O', 'CO', 'CH4', 'O2']
    return atmpro.sort_index(ascending = False)





def write_atmpro_txtfile(atmpro = None,
                         savein = 'default_atmopro.dat', unitsin = 'units'):
    '''
    Writes an atmospheric profile\'s dictionary, ATMPRO, to text file at SAVEIN.
    '''
    properties = ('altitude', 'pressure', 'temperature',
                  'H2O', 'CO2', 'O3', 'N2O', 'CO', 'CH4', 'O2')

    data_unit_tuples = ((atmpro[property]['data'], atmpro[property]['units'])
                        for property in properties)

    datas , units = itertools.zip_longest(*data_unit_tuples)

    units = tuple(
        itertools.chain(
        ('',),  #This needs to be blank for the writing of TAPE5
        (atmpro_units_tags_translate(property = properties[1],
                                     units = units[1],
                                     unitsin = unitsin),),
        (atmpro_units_tags_translate(property = properties[2],
                                     units = units[2],
                                     unitsin = unitsin),),
        atmpro_units_tags_translate(property = 'molecule',
                                    units = units[3:],
                                    unitsin = unitsin)
        ))

    datas = itertools.zip_longest(*datas)
    
    lines_to_write = collections.deque([])
    lines_to_write.extend([(len(properties) * '%15s') % units])
    lines_to_write.extend((len(data) * '%15f') % data for data in datas)

    with open(savein, mode = 'w', encoding = 'utf-8') as file:
        file.write('\n'.join(lines_to_write))
    



def OUTPUT_RADSUM_to_pandasPanel(readfrom = '', cooling_rate = False,
                                 signed_fluxes = False):
    '''
    Converts table in OUTPUT_RADSUM to a Pandas Panel
    '''
    with open(readfrom, mode = 'r', encoding = 'utf-8') as file:
        content = file.read()

    content_wbs = (content_wb.strip()
                   for content_wb in content.split('WAVENUMBER BAND')
                   if content_wb and not content_wb.isspace())

    datas = collections.deque([])
    wbranges = collections.deque([])
    for content_wb in content_wbs:
        lines = (line.strip() for line in content_wb.split('\n')
        if line and not line.isspace())
        wbranges.append(tuple(float(w)
                              for w in next(lines).split()
                              if is_number(w) and float(w) >= 0))
        [next(lines) for _ in range(3)]
        datas.append(np.array([[float(n) for n in line.split()] \
                               for line in lines if len(line.split()) == 6]))

    datas = np.array(datas)
    if cooling_rate:
        datas[:, :, -1] = - datas[:, :, -1]
        rate_label = 'cooling_rate'
    else:
        rate_label = 'heating_rate'

    if signed_fluxes:
        datas[:, : , 2] = - datas[:, :, 2]
        datas[:, :, 4] = datas[:, :, 2] + datas[:, :, 3]

    return pandas.Panel(datas[:, :, 1:],
                        items = pandas.MultiIndex.from_tuples(list(wbranges),
                                                              names = ['V1', 'V2']),
                        major_axis = datas[0, :, 0],
                        minor_axis = ('pressure', 'flux_up', 'flux_down',
                                      'net_flux', rate_label))




def sum_OUTPUT_RADSUM_over_wave_numbers(readfrom = './OUTPUT_RADSUM',
                                        V1 = 0, V2 = 100):
    '''
    Sum fluxes and cooling rates in OUTPUT_RADSUM over all
    wave numbers and return a Pandas DataFrame 
    (number of levels, ..., 0) x (pressure, flux up, flux down, net flux, coolin rate)
    INPUT:
    readfrom --- file path to OUTPUT_RADSUM
    '''
    outrad = OUTPUT_RADSUM_to_pandasPanel(readfrom = readfrom,
                                          cooling_rate = True,
                                          signed_fluxes = True)
    DV_band = outrad.items[0][1] - outrad.items[0][0]
    flux_cor_tot = outrad.ix[(V1, V1 + DV_band): (V2 - DV_band, V2), :,
                             ['flux_up', 'flux_down', 'net_flux',
                              'cooling_rate']].sum(axis = 'items')
    pressure = outrad.ix[outrad.items[0], :, 'pressure']
    return pandas.concat([pressure, flux_cor_tot], axis = 1)





def save_figures_by_property(figures, properties, savein, fmt):
    '''
    Save FIGURES corresponding to PROPERTIES in directory SAVEIN
    in format FMT
    '''
    if not os.path.isdir(savein):
        os.makedirs(savein)

    if os.path.isdir(savein) and os.listdir(savein):
        if input('{0} is non-empty.  Proceed anyway? (yes/no; y/n):  '.format(savein)) in ('yes', 'y'):
            [figure.savefig(os.path.join(savein, ''.join((property, '.', fmt))))
             for property, figure in itertools.zip_longest(properties, figures) if figure]
        else:
            return
    else:
        [figure.savefig(os.path.join(savein, ''.join((property, '.', fmt))))
             for property, figure in itertools.zip_longest(properties, figures) if figure]    
    
    


def write_pandasDataFrames_to_Excel(saveas = 'somename.xlsx', frames = [], frame_names = []):
    '''
    Save a list of Pandas DataFrames as sheets in an excel file
    Note the file extension needs to be set to xlsx, xls does not work.
    '''
    if frames:
        with pandas.ExcelWriter(saveas) as writer:
            [frame.to_excel(writer, sheet_name = name)
             for frame, name in zip(frames, frame_names)]
    else:
        print('No DataFrames to save')
        return
        






def atoms_to_MIND1(H2O = 0, CO2 = 0, O3 = 0, N2O = 0, CO = 0, CH4 = 0, O2 = 0, NO = 0,
                   SO2 = 0, NO2 = 0, NH3 = 0, HNO3 = 0, OH = 0, HF = 0, HCL = 0, HBR = 0,
                   HI = 0, CLO = 0, OCS = 0, H2CO = 0, HOCL = 0, N2 = 0, HCN = 0, CH3CL = 0,
                   H2O2 = 0, C2H2 = 0, C2H6 = 0, PH3 = 0, COF2 = 0, SF6 = 0, H2S = 0, HCOOH = 0,
                   HO2 = 0, O = 0, CLONO2 = 0, NOplus = 0, HOBR = 0, C2H4 = 0, CH3OH = 0):
    '''
    Returns a lengthy string containing only \'1\' or \'0\', indicating whether
    a gas species is ON or OFF, respectively.  The returned string can be used
    when writing TAPE5 for LNFL.
    '''
    minds = (H2O, CO2, O3, N2O, CO, CH4, O2, NO,
             SO2, NO2, NH3, HNO3, OH, HF, HCL, HBR,
             HI, CLO, OCS, H2CO, HOCL, N2, HCN, CH3CL,
             H2O2, C2H2, C2H6, PH3, COF2, SF6, H2S, HCOOH,
             HO2, O, CLONO2, NOplus, HOBR, C2H4, CH3OH)
    return ''.join(str(mind) for mind in minds)        




def atmpro_txtfile_to_PROfile(readfrom = 'atmopro.dat', saveas = 'atmopro.pro',
                              header = 'some atmospherice profile'):
    '''
    Read atmospheric profile from a text file and write and save as
    formatted Fortran (which can be included in lbl.f).

    This assumes that all quantities in the text file has tag A for units.
    For molecule species, original units [ppmv] will be converted to [g/g],
    except for CO2, which will be converted to [l/l].
    INPUT:
    readfrom --- path to text file containing atmospheric profile
    saveas   --- path to formatter Fortran file to save the same atmospheric
                 profile in
    '''
    Nrow = 5

    names = ('pressure', 'temperature',
             'H2O', 'CO2', 'O3', 'N2O', 'CO', 'CH4', 'O2')
    lbl_names = ('plevel', 'tlayer', 'wlayer', 'clayer', 'olayer', 'qlayer',
                 'rlayer', 'CH4layer', 'O2layer')
    
    data = np.loadtxt(readfrom, skiprows = 1)
    layer_data = .5 * (data[1:, 2:] + data[:-1, 2:])

    name_and_values = (
        (lbl_name, 1e-6 * d[::-1]) if name in ('CO2',)
        else (lbl_name, mixingratio_volume2mass(substance_name = name,
                                                volume_mix = 1e-6 * d[::-1]))
    if name in ('H2O', 'O3', 'N2O', 'CO', 'CH4', 'O2')
    else (lbl_name, d[::-1]) 
    for name, lbl_name, d in itertools.zip_longest(
        names, lbl_names, itertools.chain([data[:, 1]], layer_data.T)
        )
    )

    lines_to_write = collections.deque([])
    for lbl_name, values in name_and_values:
        Nvalues = values.shape[0]

        if lbl_name == 'plevel':
            headline = '{:6}data ({:}(i),i=1,nlayer+1)/'
        else:
            headline = '{:6}data ({:}(i),i=1,nlayer)/'
        
        fmtrs = ('{:12.4e}' for _ in range(Nvalues))

        fmtrs = (
        ','.join(fmtr for fmtr in fmtr_group if fmtr)
        for fmtr_group in itertools.zip_longest(*(Nrow * [fmtrs]))
        )

        lines_to_write.extend(
        [headline.format('', lbl_name),
         ''.join(
            [',\n'.join((''.join(['{:5}&'.format(''), fmtr]) for fmtr in fmtrs)),
             '/\n', 'c']).format(*values)]
        )
    lines_to_write.appendleft('c{:5}{}'.format('', header))

    with open(saveas, mode = 'w', encoding = 'utf-8') as file:
        file.write('\n'.join(lines_to_write))





    
