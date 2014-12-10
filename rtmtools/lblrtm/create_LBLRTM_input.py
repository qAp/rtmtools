import itertools
import collections
import timeit
import numpy as np
import io
import rtmtools.lblrtm.aerutils as aerutils



class ShapeMismatchError(Exception):
    pass


def molecular_species_index():
    print('''
    (M):  AVAILABLE MOLECULAR SPECIES:
    1:   H2O    2:   CO2   3:    O3   4:   N2O   5:    CO   6:   CH4   7:    O2   8:   NO
    9:   SO2   10:   NO2  11:   NH3  12:  HNO3  13:    OH  14:    HF  15:   HCL   16:  HBR
    17:    HI   18:   CLO  19:   OCS  20:  H2CO  21:  HOCL  22:    N2  23:   HCN   24: CH3CL
    25:  H2O2  26:   C2H2  27:  C2H6  28:   PH3  29:  COF2  30:   SF6  31:   H2S   32: HCOOH
    33:   HO2  34:      O  35:CLONO2  36:   NO+  37:  HOBR  38:   C2H4 39: CH3OH
    ''')


def read_atmopro_from_TAPE5():
    '''
    Extracts atmosphere profile data from
    \'aerlbl_v12.2_package/radsum/run_examples/TAPE5\' and write them to a text file.
    In columns from left to right are: altitude, pressure, temperature,
    [concentration of molecules]
    '''
    tapepath = '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/radsum/run_examples/TAPE5'
    with open(tapepath, mode = 'r', encoding = 'utf-8') as ftape:
        lines = ftape.read().split('\n')
    pro2s = ((l, lines[k + 1]) for k, l in enumerate(lines) if 'AAAAAAA' in l)
    apts, vmols = zip(*pro2s)
    aptonlys = ((altitude, pressure, temperature)
                for altitude, pressure, temperature, tags1, tags2
                in (apt.split() for apt in apts))
    vmolindvs = (tuple(''.join(num) for num in
                       itertools.zip_longest(*(10* [iter(vmol)]),
                                             fillvalue = ''))
                 for vmol in vmols)
    pro1s = (tuple(itertools.chain.from_iterable(onetwos))
             for onetwos in itertools.zip_longest(aptonlys, vmolindvs))
    line_units = ((10 * '%15s') % tuple(' AAAAAAAAA'),)
    lines_to_write = ((len(pro1)*'%15s') % pro1 for pro1 in pro1s)
    lines_to_write = itertools.chain(line_units, lines_to_write)
    with open('atmopro.dat', mode = 'w', encoding = 'utf-8') as fatmopro:
        fatmopro.write('\n'.join(lines_to_write))



def PT2altitudes(pressure = 850., temperature = 290.):
    '''
    Returns altitude from pressure and temperature
    INPUT:
    pressure --- pressure value(s) [hPa]
    temperature --- temperatures value(s) [K]
    OUTPUT:
    altitude --- altitude value(s) [km]
    '''
    if pressure.shape != temperature.shape:
        raise ShapeMismatchError

    g, R = 9.806, 287.05

    Tavg = .5 * (temperature[:-1] + temperature[1:])
    logPfrac = np.log(pressure[:-1]/ pressure[1:])
    z = R / (1000 * g) * Tavg * logPfrac
    z = np.concatenate(([0], z))
    return np.cumsum(z)


def atmopro_mls75pro(outputfilename = 'mls75pro.dat',
                     lev0_temp = 294.,
                     H2O = None, O3 = None,
                     CO2 = 0., N2O = 0., CO = 0., CH4 = 0., O2 = 0.,
                     up_to_level = 59):
    '''
    Reads atmosphere profile from mls75.pro.
    Average adjacent layer quantities: temperature, wlayer and olayer
    Assign value to the lowest level (lev0).
    Gather any additional molecules\' conc.
    Compute altitude from pressure and temperature.
    Write to text file with columns from left to right:
    altitude, pressure, temperature,
    [concentration of molecules]
    INPUT:
    outputfilename --- path for the output text file
    H2O --- H2O concentration [g/g]
    CO2 --- CO2 concentration [ml/ml]
    O3  --- O3 concentration [g/g]
    N2O --- N2O concentration [g/g]
    CO --- CO concentration [g/g]
    CH4 --- CH4 concentration [g/g]
    O2 --- O2 concentration [g/g]
    '''
    path_mls75pro = '/nuwa_cluster/home/jackyu/radiation/crd/atmosphere_profiles/mls75.pro'
    with open(path_mls75pro, mode = 'r', encoding = 'utf-8') as fmls75:
        c = fmls75.read()
        
    plevel, tlayer, wlayer, olayer = (np.array([float(n.rstrip(',/'))
                                                for n in v.split()[1:]
                                                if n.endswith(',') or n.endswith('/')])[::-1]
                                      for v in c.split('data')[1:])

    middle_tlevel = .5 * (tlayer[: -1] + tlayer[1:])
    middle_wlevel = .5 * (wlayer[: -1] + wlayer[1:])
    middle_olevel = .5 * (olayer[: -1] + olayer[1:])

    tlevel = np.concatenate(([lev0_temp], middle_tlevel, [tlayer[-1]]))
    wlevel = np.concatenate(([wlayer[0]], middle_wlevel, [wlayer[-1]]))
    olevel = np.concatenate(([olayer[0]], middle_olevel, [olayer[-1]]))

    altitudes = PT2altitudes(pressure = plevel, temperature = tlevel)
    if altitudes[-1] == np.inf:
        altitudes[-1] = 100.

    H2O = wlevel if H2O is None else H2O
    O3 = olevel if O3 is None else O3

    molecules = (H2O, CO2, O3, N2O, CO, CH4, O2)
    names = ('H2O', 'CO2', 'O3', 'N2O', 'CO', 'CH4', 'O2')
    
    #Convert CO2 from [l/l] to ppmv and the rest from [g/g] to [ppmv]
    molecules = (1e6 * molecule if molecule is CO2
                 else 1e6 * aerutils.mixingratio_mass2volume(substance_name = name,
                                                             mass_mix = molecule)
                 for name, molecule in zip(names, molecules) if not name is 'CO2')

    #Convert all into numpy arrays
    molecules = (molecule if isinstance(molecule, np.ndarray)
    else (molecule * np.ones(plevel.shape)) if isinstance(molecule, (int, float))
    else np.zeros(plevel.shape) for molecule in molecules)

    atmprofile = np.array(list(itertools.chain([altitudes, plevel, tlevel], molecules)))

    file_header = 15 * ' ' + (9 * '%15s') % tuple('AAAAAAAAA')
    np.savetxt(outputfilename, atmprofile.T[:up_to_level],
    fmt = 3 * ['%15.5f'] + 7 * ['%15.4e'],
    delimiter = '', comments = '',
    header = file_header)



def mls75pro_lbl_aer_combined(saveas = './lbl_aer_profiles.dat',
                              lev0_temp = 294.,
                              H2O = None, O3 = None,
                              CO2 = 0., N2O = 0., CO = 0., CH4 = 0., O2 = 0.,
                              up_to_level = 59):
    '''
    Writes to file the numbers used by lbl and aer for
    the mls75pro atmosphere profile.
    
    For comparison, the units in mls75.pro are used.
    '''
    path_mls75pro = '/nuwa_cluster/home/jackyu/line_by_line/lbl/mls75.pro'
    with open(path_mls75pro, mode = 'r', encoding = 'utf-8') as fmls75:
        c = fmls75.read()
        
    plevel, tlayer, wlayer, olayer = (np.array([float(n.rstrip(',/'))
                                                for n in v.split()[1:]
                                                if n.endswith(',') or n.endswith('/')])[::-1]
    for v in c.split('data')[1:])
    
    middle_tlevel = .5 * (tlayer[: -1] + tlayer[1:])
    middle_wlevel = .5 * (wlayer[: -1] + wlayer[1:])
    middle_olevel = .5 * (olayer[: -1] + olayer[1:])
    
    tlevel = np.concatenate(([lev0_temp], middle_tlevel, [tlayer[-1]]))
    wlevel = np.concatenate(([wlayer[0]], middle_wlevel, [wlayer[-1]]))
    olevel = np.concatenate(([olayer[0]], middle_olevel, [olayer[-1]]))
    
    altitudes = PT2altitudes(pressure = plevel, temperature = tlevel)
    if altitudes[-1] == np.inf:
        altitudes[-1] = 100.
        
    H2O = wlevel if H2O is None else H2O
    O3 = olevel if O3 is None else O3
    
    molecules = (H2O, CO2, O3, N2O, CO, CH4, O2)
    names = ('H2O', 'CO2', 'O3', 'N2O', 'CO', 'CH4', 'O2')
    
    molecules = (molecule if isinstance(molecule, np.ndarray)
                 else (molecule * np.ones(plevel.shape)) if isinstance(molecule, (int, float))
    else np.zeros(plevel.shape) for molecule in molecules)
    
    atmprofile = np.array(list(itertools.chain([altitudes, plevel, tlevel], molecules)))

    lblprofile = np.concatenate(
    (-999. * np.ones((2, tlayer.shape[-1])),
     np.array([tlayer, wlayer, 350e-6 * np.zeros(wlayer.shape), olayer])
     ), axis = 0)
    
    aer_lbl_profiles = np.insert(atmprofile.T[:, :6], obj = np.arange(1, atmprofile.T.shape[0]),
    values = lblprofile.T,
    axis = 0)

    if saveas.endswith('.csv'):
        np.savetxt(saveas, aer_lbl_profiles[: 2 * (up_to_level - 1) + 1, :6],
                   fmt = 3 * ['%15.5f'] + 3 * ['%15.4e'],
                   delimiter = ',', comments = '', header = '')
    else:
        np.savetxt(saveas, aer_lbl_profiles[: 2 * (up_to_level - 1) + 1, :6],
                   fmt = 3 * ['%15.5f'] + 3 * ['%15.4e'],
                   delimiter = '', comments = '', header = '')



def double_atmpro_layers(filepath_original = 'atmopro.dat',
                         filepath_doubled = 'atmopro_layersX2.dat'):
    '''
    Insert values averaged between adjacent levels into the atmospheric
    profile and write the resulting profile, which has twice as many layers,
    to a text file.
    INPUT:
    filepath_original --- filepath of the original atmospheric profile
    filepath_doubled  --- filepath of the resulting atmospheric profile
    '''
    with open(filepath_original, mode = 'r', encoding = 'utf-8') as forg:
        line_units = forg.readline()
        content = forg.read()

    atmopro_original = np.array([[float(n) for n in line.split()] for line in content.split('\n')])
    atmopro_inbetween = .5 * (atmopro_original[:-1] + atmopro_original[1:])
    atmopro_weaved = np.insert(atmopro_original,
                               np.arange(1, atmopro_original.shape[0]),
                               atmopro_inbetween, axis = 0)

    np.savetxt(filepath_doubled, atmopro_weaved, delimiter = '',
               fmt = 3 * ['%15.3f'] + 7 * ['%15.4e'],
               comments = '',
               header = line_units)


def atmopro_mls75pro_offsetP():
    '''
    Add atmopro.dat\'s top-level pressure to mls75pro.dat\s
    pressures such that they both have the same lowest pressure.
    '''
    filename_atmopro, filename_mls75pro = 'atmopro.dat', 'mls75pro.dat'
    filename_mls75pro_offsetP = 'mls75pro_offsetP.dat'
    atmopro_mls75pro()
    read_atmopro_from_TAPE5()

    atmopro = aerutils.read_atmpro_txtfile(filename_atmopro)
    mlspro  = aerutils.read_atmpro_txtfile(filename_mls75pro)

    mlspro['pressure']['data'] = mlspro['pressure']['data'] + atmopro['pressure']['data'][-1]

    aerutils.write_atmpro_txtfile(atmpro = mlspro, savein = filename_mls75pro_offsetP,
                                  unitsin = 'tags')






'''
lblrtm\'s TAPE5
'''

def record_1_1(CXID):
    'Returns 80 characters of user identification'
    L = 80
    if len(CXID) > 78:
        raise InputError('User identification cannot be longer than 78.')
    return '{0:2}{1:78}'.format('$ ', CXID)


def record_1_2(IHIRAC = '', ILBLF4 = '', ICNTNM = '', IAERSL = '',
               IEMIT = '', ISCAN = '', IFILTR = '', IPLOT = '',
               ITEST = '',  IATM = '',  IMRG = '',  ILAS = '',
               IOD = '', IXSECT = '',  MPTS = '', NPTS = ''):
    '''
    instructions
    '''
    notes = (
        (4, '{0:>4}', 'HI='), (1, '{0:d}', IHIRAC),
        (4, '{0:>4}', 'F4='), (1, '{0:d}', ILBLF4),
        (4, '{0:>4}', 'CN='), (1, '{0:d}', ICNTNM),
        (4, '{0:>4}', 'AE='), (1, '{0:d}', IAERSL),
        (4, '{0:>4}', 'EM='), (1, '{0:d}', IEMIT),
        (4, '{0:>4}', 'SC='), (1, '{0:d}', ISCAN),
        (4, '{0:>4}', 'FI='), (1, '{0:d}', IFILTR),
        (4, '{0:>4}', 'PL='), (1, '{0:d}', IPLOT),
        (4, '{0:>4}', 'TS='), (1, '{0:d}', ITEST),
        (4, '{0:>4}', 'AM='), (1, '{0:d}', IATM),
        (3, '{0:>3}', 'MG'), (2, '{0:>2d}', IMRG),
        (4, '{0:>4}', 'LA='), (1, '{0:d}', ILAS),
        (4, '{0:>4}', 'OD='), (1, '{0:d}', IOD),
        (4, '{0:>4}', 'XS='), (1, '{0:d}', IXSECT),
        (1, '', ''), (4, '{0:=4d}', MPTS),
        (1, '', ''), (4, '{0:=4d}', NPTS)
        )
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def record_1_2_1(INFLAG = None, IOTFLG = None, JULDAT = None):
    '''
    INFLAG --- input flag for solar radiance calculation
    IOTFLG --- output flag for solar radiance calculation
    JULDAT --- JULDAT
    '''
    notes = ((5, '{:>5d}', INFLAG),
             (5, '{:>5d}', IOTFLG),
             (2, None, None),
             (3, '{:>3d}', JULDAT))
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)



def record_1_3(V1 = '', V2 = '',
               SAMPLE = '', DVSET = '', ALFAL0 = '', AVMASS = '',
               DPTMIN = '', DPTFAC = '', ILNFLG = '', DVOUT = '',
               NMOL_SCAL = ''):
    '''
    V1     --- beginning wavenumber value for the calculation
               (VLAS = V1 for ILAS = 1,2)
    V2     --- ending wavenumber value for the calculation
               ( (V2-V1) must be less than 2020 cm - 1 )
    SAMPLE --- number of sample points per mean halfwidth (between 1. and 4.)
               (default = 4.)
    DVSET  --- selected DV for the final monochromatic calculation if positive,
               must be within 20% of DV for final monochromatic calculation
               determined by LBLRTM
    ALFAL0 --- average collision broadened halfwidth (cm - 1/atm) (default = 0.04)
    AVMASS --- average molecular mass (amu) for Doppler halfwidth (default = 36)
    DPTMIN --- minimum molecular optical depth below which lines will be rejected
               (negative value defaults to DPTMIN = 0.0002)
    DPTFAC --- factor multiplying molecular continuum optical depth
               to determine optical depth below which lines will be rejected
               (negative value defaults to DPTFAC = 0.001)
    ILNFLG --- flag for binary record of line rejection information
               = 0  line rejection information not recorded (default)
               = 1  write line rejection information to REJ1, REJ4
               = 2  read line rejection information from REJ1, REJ4
    DVOUT  --- selected DV grid for the optical depth "monochromatic" output spacing
               (must be less than or equal to default spacing or DVSET if nonzero).
    NMOL_SCAL --- Enables the scaling of the atmospheric profile for selected species
                  NMOL_SCAL is the highest molecule number for which scaling will be
                  applied. See Record(s) 1.3.a/1.3.b.n
    '''
    notes = (
        (10, '{0:>10.4f}', V1), (10, '{0:10.4f}', V2),
        (10, '{0:>10.4f}', SAMPLE),
        (10, '{0:>10.4f}', DVSET),
        (10, '{0:>10.4f}', ALFAL0),
        (10, '{0:>10.4f}', AVMASS),
        (10, '{0:>10.4f}', DPTMIN),
        (10, '{0:>10.4f}', DPTFAC),
        (4, '', ''),
        (1, '{0:1d}', ILNFLG),
        (5, '', ''),
        (10, '{0:>10.4f}', DVOUT),
        (3, '', ''),
        (2, '{0:2d}', NMOL_SCAL)
        )
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def record_1_4(TBOUND = '',
               SREMIS1 = '', SREMIS2 = '', SREMIS3 = '',
               SRREFL1 = '', SRREFL2 = '', SRREFL3 = '',
               surf_refl = ''):
    '''
    TBOUND    --- temperature of boundary (K)
    SREMIS(I) --- frequency dependent boundary emissivity coefficients (I = 1,2,3)
                  EMISSIVITY   = SREMIS(1) + SREMIS(2)*V + SREMIS(3)*(V**2)
                  *** NOTE: Entering a value for SREMIS(1) < 0 allows for direct
                  input of boundary emissivities from file \'EMISSIVITY\'
    SRREFL(I) --- frequency dependent boundary reflectivity coefficients (I = 1,2,3)
                  REFLECTIVITY = SRREFL(1) + SRREFL(2)*V + SRREFL(3)*(V**2)
                  *** NOTE: Entering a value for SRREFL(1) < 0 allows for direct
                  input of boundary reflectivities from file \'REFLECTIVITY\'
    surf_refl --- specifies the surface type used in computing the reflected downward
                  radiance
                  
                  \'s\' or \' \' - is for a specular surface
                  \'l\'         - is for a lambertian surface
                  Note:  For the surf_refl = \'l\' option
                  If IATM=0 the appropriate angle is specified on  Record 2.1;
                  Otherwise the angle is determined from the geometry in lblatm
                  (IATM>0)
    '''
    notes = ((10, '{0:>10.3f}', TBOUND),
             (10, '{0:>10.3f}', SREMIS1),
             (10, '{0:>10.3f}', SREMIS2),
             (10, '{0:>10.3f}', SREMIS3),
             (10, '{0:>10.3f}', SRREFL1),
             (10, '{0:>10.3f}', SRREFL2),
             (10, '{0:>10.3f}', SRREFL3),
             (4, '', ''),
             (1, '{0:1s}', surf_refl))
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def record_1_6a(PTHODL = '', LAYTOT = ''):
    '''
    PTHODL --- pathname for precalculated optical depth files
               Example:  For PTHODL="ODdeflt_", code will look for files
               ODdeflt_01, ...
    LAYTOT --- total number of layers used in radiative transfer
               *** NOTE *** LAYTOT ignored for IEMIT = 3
    '''
    notes = ((55, '{0:55s}', PTHODL),
             (1, '', ''),
             (4, '{0:>4d}', LAYTOT))
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def record_3_1(MODEL = '', ITYPE = '', IBMAX = '', ZERO = '',
               NOPRNT = '', NMOL = '', IPUNCH = '', IFXTYP = '',
               MUNITS = '', RE = '', HSPACE = '', VBAR = '', REF_LAT = ''):
    '''
    TL;DR
    '''
    notes = ((5, '{0:>5d}', MODEL),
             (5, '{0:>5d}', ITYPE),
             (5, '{0:>5d}', IBMAX),
             (5, '{0:>5d}', ZERO),
             (5, '{0:>5d}', NOPRNT),
             (5, '{0:>5d}', NMOL),
             (5, '{0:>5d}', IPUNCH),
             (2, '{0:>2d}', IFXTYP),
             (1, '', ''),
             (2, '{0:>2d}', MUNITS),
             (10, '{0:>10.3f}', RE),
             (10, '{0:>10.3f}', HSPACE),
             (10, '{0:>10.3f}', VBAR),
             (10, '', ''), (10, '{0:>10.3f}', REF_LAT))
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def record_3_2(H1 = '', H2 = '', ANGLE = '', RANGE = '',
               BETA = '', LEN = '', HOBS = ''):
    '''
    H1    --- observer altitude (km). If IBMAX is negative, H1 is provided in
              pressure units (mbars)
    ANGLE --- zenith angle at H1 (degrees)
    '''
    notes = (
        (10, '{0:>10.4f}', H1), (10, '{0:>10.4f}', H2),
        (10, '{0:>10.4f}', ANGLE),
        (10, '{0:>10.3f}', RANGE),
        (10, '{0:>10.3f}', BETA),
        (5, '{0:>5d}', LEN),
        (5, '', ''),
        (10, '{0:>10.3f}', HOBS))
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def record_3_3B(*altitudes):
    '''
    ZBND(I), I=1, IBMAX   altitudes of LBLRTM layer boundaries
    '''
    Nrow, Naltitudes = 8, len(altitudes)
    return ''.join('{0:10.3f}\n'.format(altitude)
                   if k not in (0, Naltitudes - 1) and (k + 1) % Nrow == 0
                   else '{0:10.3f}'.format(altitude)
                   for k, altitude in enumerate(altitudes))
    
    
def record_3_4(IMMAX = '', HMOD = ''):
    '''
    IMMAX --- number of atmospheric profile boundaries
    HMOD  --- 24 character description of profile
    '''
    notes = ((5, '{0:5d}', IMMAX),
             (24, '{0:>24s}', HMOD))
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def record_3_5(ZM = '', PM = '', TM = '', JCHARP = '',
               JCHART = '', JLONG = '', JCHAR = ''):
    '''
    ZM       --- boundary altitude [km]
    PM       --- pressure (units and input options set by JCHARP)
    TM       --- temperature (units and input options set by JCHART)
    JCHARP   --- flag for units and input options for pressure (see Table I)
    JCHART   --- flag for units and input options for temperature (see Table I)
    JLONG    --- flag for reading long record for molecular information
                 (= L  read VMOL(M) in 8E15.8 format)
    JCHAR(K) --- flag for units and input options for the K\'th molecule (see Table I)
    '''
    notes = ((10, '{0:10.3f}', ZM),
             (10, '{0:10.3f}', PM),
             (10, '{0:10.3f}', TM),
             (5, '', ''),
             (1, '{0:1s}', JCHARP),
             (1, '{0:1s}', JCHART),
             (1, '', ''),
             (1, '{0:1s}', JLONG),
             (1, '', ''),
             (39, '{0:<39s}', JCHAR)
             )
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def record_3_6(JLONG, *vmols):
    '''
    VMOL(M), M=1, NMOL
    VMOL(M) -- density of the M\'th molecule in units set by JCHAR(K)
               **NOTE** If JLONG=L, then VMOL(M) is in 8E15.8 format
    '''
    return ''.join('{0:15.8e}'.format(vmol)
                   if JLONG is 'L' else '{0:10.4e}'.format(vmol)
for vmol in vmols)


def record_6(HWHM = '', V1 = '', V2 = '', JEMIT = '',
             JFN = '', JVAR = '', SAMPL = '', NNFILE = '',
             NPTS = ''):
    '''
    HWHM   --- (Half Width Half Maximum)
               Note: HWHM is first zero crossing of periodic functions for JFN < 0.
               HWHM is redefined as  HWHM=(FIRST ZERO)/(PI/SCALE)
    V1     --- beginning wavenumber value for performing SCAN
    V2     --- ending wavenumber value for performing SCAN
    JEMIT      =  0  SCAN convolved with transmission
               =  1  SCAN convolved with radiance
    JFN    --- selects choice of scanning function
    JVAR   --- flag for variable HWHM
               = 0 no variation
               = 1 HWHM(vi) = HWHM(v1) * (vi / v1)
    SAMPL  --- number of sample points per half width
               = 0 gives default value for each function
               < 0 this variable specifies the output spectral spacing (DELVO cm-1)
               The value of SAMPL is calculated internally as SAMPL = HWHM/DELVO
    NNFILE --- unit number for scanned sequential output
               defaults to NFILE (= 13) or previous value of NNFILE if doing multiple
               LBLRTM run
    NPTS   --- number of values to be printed for the beginning and ending of each
               panel for current scanned file
    '''
    notes = ((10, '{0:10.3f}', HWHM),
             (10, '{0:10.3f}', V1), (10, '{0:10.3f}', V2),
             (3, '', ''),
             (2, '{0:2d}', JEMIT),
             (3, '', ''),
             (2, '{0:2d}', JFN),
             (3, '', ''),
             (2, '{0:2d}', JVAR),
             (10, '{0:10.4f}', SAMPL),
             (15, '', ''),
             (5, '{0:5d}', NNFILE),
             (5, '{0:5d}', NPTS))
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)



def record_6_1(DIRCOS = ''):
    '''
    DIRCOS --- direction cosine of radiance computation for external calculation of
               fluxes from Gaussian quadrature summation over one or more angles.
    '''
    notes = ((10, '{0:10.8f}', DIRCOS),)
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)    


def record_12_2A(V1 = None, V2 = None, XSIZE = None, DELV = None, 
                 NUMSBX = None, NOENDX = None, LFILE = None, LSKIPF = None,
                 SCALE = None, IOPT = None, I4P = None, IXDEC = None):
    '''
    V1    --- initial wavenumber of the plot
    V2    --- the final wavenumber of the plot
    XSIZE --- number of inches of the X-axis
    DELV  --- number of wavenumbers (cm-1) per major divison
    '''
    notes = ((10, '{:>10.4f}', V1),
             (10, '{:>10.4f}', V2),
             (10, '{:>10.4f}', XSIZE),
             (10, '{:>10.4f}', DELV),
             (5,  '{:>5d}', NUMSBX),
             (5, '{:>5d}', NOENDX),
             (5, '{:>5d}', LFILE),
             (5, '{:>5d}', LSKIPF),
             (5, '{:>10.3f}', SCALE),
             (5, '{:>2d}', IOPT),
             (5, '{:>3d}', I4P),
             (5, '{:>5d}', IXDEC))
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)    



def record_12_3A(YMIN = None, YMAX = None, YSIZE = None, DELY = None,
                 NUMSBY = None, NOENDY = None, IDEC = None,
                 JEMIT = None, JPLOT = None, LOGPLT = None,
                 JHDR = None, JOUT = None, JPLTFL = None):
    '''
    YMIN --- Y value at bottom of Y-axis
    YMAX --- Y value at top of Y-axis
    YSIZE --- number of inches for the Y-aixs
    etc.
    '''
    notes = ((10, '{:>10.4f}', YMIN),
             (10, '{:>10.4f}', YMAX),
             (10, '{:>10.3f}', YSIZE),
             (10, '{:>10.3f}', DELY),
             (5, '{:>5d}', NUMSBY),
             (5, '{:>5d}', NOENDY),
             (5, '{:>5d}', IDEC),
             (5, '{:>5d}', JEMIT),
             (5, '{:>5d}', JPLOT),
             (5, '{:>5d}', LOGPLT),
             (2, '{:>2d}', JHDR),
             (3, None, None),
             (2, '{:>2d}', JOUT),
             (3, '{:>3d}', JPLTFL))
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)    



def write_fluxcalc_TAPE5(atmpro = 'atmopro.dat',
                         V1 = 8., V2 = 2002.,
                         JLONG = '',
                         TBOUND = 288.2,
                         CXID = 'GARANDProfile(CanadianStudy):6 ',
                         ICNTNM = 1,
                         TAPE5name = 'TAPE5'):
    '''
    Writes a TAPE5 for \'flux calcuations\' with LBLRTM, like the one in
    aerlbl_v12.2_package/radsum/run_examples.
    INPUT:
    atmpro     --- path to file containing atmosphere profile
    TAPE5name  --- name of output TAPE5 (default = \'TAPE5\')
    V1         --- beginning wavenumber value for the calculation
    V2         --- ending wavenumber value for the calculation
    JLONG      --- flag for reading long record for molecular information
                   = L read VMOL(M) in 8E15.8 format
    TBOUND     --- temperature of boundary [K]
    ICNTNM     --- (0,1,2,3,4,5,6) flag for continuum (CONTNM)
                   = 0  no continuum calculated
                   = 1  all continua calculated, including Rayleigh extinction where applicable
                   = 2  H2O self not calculated, all other continua/Rayleigh extinction calculated
                   = 3  H2O foreign not calculated, all other continua/Rayleigh extinction calculated
                   = 4  H2O self and foreign not calculated, all other continua/Rayleigh
                        extinction calculated
                   = 5  Rayleigh extinction not calculated, all other continua calculated
                   = 6  Individual continuum scale factors input (Requires Record 1.2a)
    CXID       --- 80 characters of user identification
    '''
    with open(atmpro, mode = 'r', encoding = 'utf-8') as fatmpro:
        line_units = fatmpro.readline()
        content = fatmpro.read()

    atmpro_units = io.StringIO(line_units.rstrip().replace(' ', ''))
    JCHARP, JCHART, JCHAR = atmpro_units.read(1), atmpro_units.read(1), atmpro_units.read()

    atmpro_lvls = (map(float, line.split()) for line in content.split('\n') if line)
    atmpro_vars = itertools.zip_longest(*atmpro_lvls)
    atmpro_altitudes = next(atmpro_vars)
    atmpro_pressures = next(atmpro_vars)
    atmpro_levels = ((next(p), next(p), next(p), tuple(p)) for p in
                     (iter(level)
                      for level in itertools.zip_longest(atmpro_altitudes,
                                                         atmpro_pressures, *atmpro_vars)))

    IMMAX = IBMAX = len(atmpro_altitudes)
    LAYTOT = IMMAX - 1
    
    lblrtm_lines = [record_1_1(CXID),
                    record_1_2(IHIRAC = 1, ILBLF4 = 1, ICNTNM = ICNTNM, IAERSL = 0,
                               IEMIT = 0, ISCAN = 0, IFILTR = 0, IPLOT = 0,
                               ITEST = 0, IATM = 1, IMRG = 1, ILAS = 0,
                               IOD = 0, IXSECT = 0, MPTS = 0, NPTS = 0),
                    record_1_3(V1 = V1, V2 = V2,
                               DPTMIN = 0.000, DPTFAC = 0.001),
                    record_3_1(MODEL = 0, ITYPE = 2, IBMAX = - IBMAX,
                               ZERO = 1, NOPRNT = 0, NMOL = 7, IPUNCH = 1,
                               IFXTYP = 0, MUNITS = 0, RE = 6356.910,
                               HSPACE = 100., VBAR = .5 * (V1 + V2), REF_LAT = 30.),
                    record_3_2(H1 = atmpro_pressures[-1], H2 = atmpro_pressures[0],
                               ANGLE = 180.0000),
                    record_3_3B(*atmpro_pressures),
                    record_3_4(IMMAX = - IMMAX)]
    
    user_profile_lines = itertools.chain.from_iterable(
        (record_3_5(ZM = altitude, PM = pressure, TM = temperature,
                    JCHARP = JCHARP, JCHART = JCHART, JLONG = JLONG, JCHAR = JCHAR),
         record_3_6(JLONG, *vmols))
        for altitude, pressure, temperature, vmols in atmpro_levels)

    output_lines = itertools.chain.from_iterable(
        ('$',
         record_1_2(IHIRAC = 0, ILBLF4 = 0, ICNTNM = 0, IAERSL = 0,
                    IEMIT = 1, ISCAN = 0, IFILTR = 0, IPLOT = 0,
                    ITEST = 0, IATM = 1, IMRG = imrg, ILAS = 0,
                    MPTS = 0, NPTS = 0),
         record_1_3(V1 = V1, V2 = V2, DPTMIN = -1, DPTFAC = -1),
         record_1_4(TBOUND = tbound, SREMIS1 = sremis1),
         record_1_6a(PTHODL = 'ODdeflt_', LAYTOT = LAYTOT),
         record_6(HWHM = 0.25, V1 = np.ceil(V1 + 1.75), V2 = np.floor(V2 - 1.75),
                  JEMIT = 1, JFN = 0, NNFILE = nnfile, NPTS = 00),
         record_6_1(DIRCOS = dircos))
        for imrg, tbound, sremis1, nnfiles
        in zip((35, 36), (0., TBOUND), (0, 1), ((31, 32, 33), (61, 62, 63)))
        for dircos, nnfile
        in zip((0.91141204, 0.59053314, 0.21234054), nnfiles))
    
    lines_to_write = collections.deque([])
    lines_to_write.extend(lblrtm_lines)
    lines_to_write.extend(user_profile_lines)
    lines_to_write.extend(output_lines)
    lines_to_write.append('%%%%%')
        
    with open(TAPE5name, mode = 'w', encoding = 'utf-8') as ftape:
        ftape.writelines('\n'.join(lines_to_write))



def write_solar_downwelling_TAPE5(CXID = 'solar downwelling',
                                  atmpro = None,
                                  ICNTNM = 0,
                                  V1 = 20000, V2 = 22000,
                                  MODEL = 2,
                                  H1 = 0, H2 = 100, ANGLE = 0.,
                                  ):
    '''
    Returns a long string of TAPE5 in the solar downwelling
    example that came with LBLRTM
    '''
    if MODEL == 0:
        IBMAX = IMMAX = - len(atmpro.index)
        bound_zp = atmpro['pressure'][:: -1]
    elif MODEL == 2:
        print('Using internal mid-latitude summer model')
        IBMAX = IMMAX = 19
        bound_zp = np.fromstring('0.00 1.00 2.00 3.00 4.00 5.00 6.00 7.00\
                8.00      9.00     10.00     11.00     20.00     30.00 \
                50.00 70.00  80.00     90.00    100.00',
                               dtype = '<f8', sep = ' ')
    
    lines = collections.deque([])
        
    lines.append(
        record_1_1(CXID))
    lines.append(
        record_1_2(IHIRAC = 1, ILBLF4 = 1, ICNTNM = ICNTNM, IAERSL = 0,
                   IEMIT = 1, ISCAN = 0, IFILTR = 0, IPLOT = 0,
                   ITEST = 0,  IATM = 1,  IMRG = 0,  ILAS = 0,
                   IOD = 0, IXSECT = 0,  MPTS = 0, NPTS = 0))
    lines.append(
        record_1_3(V1 = V1, V2 = V2,
                   SAMPLE = '', DVSET = '', ALFAL0 = '', AVMASS = '',
                   DPTMIN = '', DPTFAC = '', ILNFLG = '', DVOUT = '',
                   NMOL_SCAL = ''))
    lines.append(
        record_1_4(TBOUND = 0,
                   SREMIS1 = 0, SREMIS2 = 0, SREMIS3 = 0,
                   SRREFL1 = 0, SRREFL2 = 0, SRREFL3 = 0,
                   surf_refl = 's'))
    lines.append(
        record_3_1(MODEL = MODEL, ITYPE = 2, IBMAX = IBMAX, ZERO = 0,
                   NOPRNT = 0, NMOL = '', IPUNCH = '', IFXTYP = '',
                   MUNITS = '', RE = '', HSPACE = '', VBAR = '', REF_LAT = ''))
    lines.append(
        record_3_2(H1 = H1, H2 = H2, ANGLE = ANGLE, RANGE = '',
                   BETA = '', LEN = '', HOBS = ''))
    lines.append(record_3_3B(*bound_zp))
        
    if MODEL == 0:
            lines.append(record_3_4(IMMAX = IMMAX))
            for i in atmpro.index[:: -1]:
                lines.append(
                    record_3_5(ZM = atmpro.loc[i, 'altitude'],
                               PM = atmpro.loc[i, 'pressure'],
                               TM = atmpro.loc[i, 'temperature'],
                               JCHARP = 'A',
                               JCHART = 'A', JLONG = 'L', JCHAR = 'AAAAAAA'))
                lines.append(
                    record_3_6('L',
                               *[atmpro.loc[i, molecule] \
                                 for molecule in ['H2O', 'CO2', 'O3',\
                                                  'N2O', 'CO', 'CH4', 'O2']]))
            
    lines.append('-1.')
        
    lines.append(
        record_1_1('Convolve transmittance with solar source function'))
    lines.append(
        record_1_2(IHIRAC = 0, ILBLF4 = 0, ICNTNM = 0, IAERSL = 0,
                   IEMIT = 2, ISCAN = 0, IFILTR = 0, IPLOT = 0,
                   ITEST = 0,  IATM = 0,  IMRG = 0,  ILAS = 0,
                   IOD = 0, IXSECT = 0,  MPTS = 0, NPTS = 0))
    lines.append(record_1_2_1(INFLAG = 0, IOTFLG = 0, JULDAT = 0))
    
    lines.append('-1.')
    
    lines.append(
        record_1_1('Transfer to ASCII plotting data (TAPES 27 and 28)'))
    lines.append(
        record_1_2(IHIRAC = 0, ILBLF4 = 0, ICNTNM = 0, IAERSL = 0,
                   IEMIT = 0, ISCAN = 0, IFILTR = 0, IPLOT = 1,
                   ITEST = 0,  IATM = 0,  IMRG = 0,  ILAS = 0,
                   IOD = 0, IXSECT = 0,  MPTS = 0, NPTS = 0))
    lines.append('# Plot title not used')
    lines.append(
        record_12_2A(V1 = V1, V2 = V2, XSIZE = 10.2, DELV = 100, 
                     NUMSBX = 5, NOENDX = 0, LFILE = 13, LSKIPF = 0,
                     SCALE = 1.0, IOPT = 0, I4P = 0, IXDEC = 0))
    lines.append(
        record_12_3A(YMIN = 0, YMAX = 1.2, YSIZE = 7.02, DELY = .2,
                     NUMSBY = 4, NOENDY = 0, IDEC = 1,
                     JEMIT = 1, JPLOT = 0, LOGPLT = 0,
                     JHDR = 0, JOUT = 3, JPLTFL = 27))
    lines.append('-1.')
    lines.append('%%%%%%%')
    return '\n'.join(lines)




'''
RADSUM\'s IN_RADSUM
'''

def IN_RADSUM_record_1(V1 = 10.0, V2 = 2000.,
                       OUTINRAT = 3980, NANG = 3, NLEV = 43,
                       TBND = 288.2, IQUAD = 0):
    '''
    V1              The beginning wavenumber of the first output group
    V2              The ending wavenumber of the final output group
    
    '''
    notes = ((10, '{:10.2f}', V1), (10, '{:10.2f}', V2),
             (5, '{:5d}', OUTINRAT), (5, '{:5d}', NANG), (5, '{:5d}', NLEV),
             (8, '{:8.1f}', TBND), (5, '{:5d}', IQUAD))
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def write_IN_RADSUM(atmpro = 'atmopro.dat',
                    V1 = 10.0, V2 = 2000.,
                    OUTINRAT = 3980, NANG = 3, IQUAD = 0):
    '''
    TBND in IN_RADSUM is set to the temperatuer of the lowest level
    in the user-provided atmospheric profile
    NLEV is the number of levels in the user-provided atmospheric profile
    '''
    with open(atmpro, mode = 'r', encoding = 'utf-8') as file:
        file.readline()
        content = file.read()

    atmpro_data = np.array([line.split() for line in content.split('\n') if line], dtype = np.float64)
    NLEV, TBND = atmpro_data.shape[0], atmpro_data[0, 2]

    lines_to_write = [
        IN_RADSUM_record_1(V1 = V1, V2 = V2,
                           OUTINRAT = OUTINRAT, NANG = NANG, NLEV = NLEV,
                           TBND = TBND, IQUAD = IQUAD)
        ]
    with open('IN_RADSUM', mode = 'w', encoding = 'utf-8') as file:
        file.write('\n'.join(lines_to_write))
        


'''
LNFL\'s TAPE5
'''

def LNFL_TAPE5_record_1(XID = ''):
    '''
    XID --- 72 characters of user identification  (9A8)
    '''
    return '$ {XID:70s}'.format(XID = XID)


def LNFL_TAPE5_record_2(VMIN = 0., VMAX = 3000.):
    '''
    VMIN --- low wavenumber limit for the line file [cm-1]
             VMIN should be 25 cm-1 less than V1 for LBLRTM calculation

    VMAX --- high wavenumber limit for the line file [cm-1]
             VMAX should be 25 cm-1 greater than V2 for LBLRTM calculation
    '''
    notes = ((10, '{:10.3f}', VMIN), (10, '{:10.3f}', VMAX))
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)


def LNFL_TAPE5_record_3(MIND1 = 39 * '0',
                        HOLIND1 = ''):
    '''
    MIND1(M) --- Molecular INDicator for Molecule M from line data on file TAPE1
                 0  molecule M is not selected
                 1  molecule M is selected

    HOLIND1 --- HOLlerith INDicator to select general LNFL options and specific options for TAPE1

                LNOUT: selects option to provide formatted representation of TAPE3 on file TAPE7
                       representation is identical to TAPE1 and TAPE2, one transition per record
                       *** CAUTION *** this option may produce a VERY LARGE output file
    
                NOCPL: suppresses all line coupling information on TAPE3 and TAPE7
    
                NLTE:  preserves transition parameters for LBLRTM
                       Non Local Thermodynamic Equilibrium (NLTE) option
    
                REJ:  selects line rejection and requires input data for
                      strength rejection (record 5)
    
                MRG2:  line parameters on TAPE2 are to be merged with those on TAPE1
    
                F160:  selects the 160 character format for TAPE1 (e.g. HITRAN_2004)
    
                BLK1:  indicates TAPE1 is blocked  (Note: NBLK1 is ignored)
    
                **       H86T1  omits SHIFT line coupling information in 1986 HITRAN or later from TAPE1
    
                **       Not available in this version of LNFL
    '''
    notes = (
        (39, '{:39s}', MIND1),
        (4, '', ''),
        (40, '{:40s}', HOLIND1)
        )
    return ''.join(fmtspec.format(value) if value != '' else length*' '
                   for length, fmtspec, value in notes)

    
def write_LNFL_TAPE5(XID = '',
                     VMIN = 0., VMAX = 3000.,
                     MIND1 = 39 * '0',
                     HOLIND1 = 'LNOUT'):
    '''
    Writes out TAPE5 for LNFL
    '''
    lines_to_write = [
        LNFL_TAPE5_record_1(XID = XID),
        LNFL_TAPE5_record_2(VMIN = VMIN, VMAX = VMAX),
        LNFL_TAPE5_record_3(MIND1 = MIND1,
                            HOLIND1 = HOLIND1)
        ]
    lines_to_write.append('%%%%%')
    with open('TAPE5', mode = 'w', encoding = 'utf-8') as file:
        file.write('\n'.join(lines_to_write))




    
    






if __name__ == '__main__':
    ww = double_atmpro_layers()
    
    

    



        

