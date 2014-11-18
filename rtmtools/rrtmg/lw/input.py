import os
import itertools
import collections
import pandas as pd



'''
INPUT_RRTM records.  
'''


def record_1_1(CXID = None):
    '''Returns 80 characters of user identification'''
    L = 80
    if CXID and len(CXID) > 78:
        raise InputError('User identification\
        cannot be longer than 78.')
    return '{0:2}{1:78}'.format('$ ', CXID or '')


def record_1_2(IAER = None,
               IATM = None,
               IXSECT = None,
               NUMANGS = None,
               IOUT = None,
               IDRV = None,
               IMCA = None,
               ICLD = None):
    notes = ((18, None, None),
             (2, '{:>2d}', IAER),
             (29, None, None),
             (1, '{:d}', IATM),
             (19, None, None),
             (1, '{:d}', IXSECT),
             (13, None, None),
             (2, '{:>2d}', NUMANGS),
             (2, None, None),
             (3, '{:>3d}', IOUT),
             (1, None, None),
             (1, '{:d}', IDRV),
             (1, None, None),
             (1, '{:d}', IMCA),
             (1, '{:d}', ICLD))
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)



def record_1_4(TBOUND = None,
               IEMIS = None,
               IREFLECT = None,
               SEMISS = None):
    notes = tuple([(10, '{:>10.3e}', TBOUND),
                   (1, None, None),
                   (1, '{:d}', IEMIS),
                   (2, None, None),
                   (1, '{:d}', IREFLECT),] + \
                  [(5, '{:>5.3e}', semis) \
                   for semis in SEMISS or 16 * [None]])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_1_4_1(DTBOUND = None):
    notes = (
        (10, '{:10.3e}', DTBOUND)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_2_1(IFORM = None,
               NLAYRS = None,
               NMOL = None):
    notes = (
        (1, None, None),
        (1, '{:d}', IFORM),
        (3, '{:>3d}', NLAYERS),
        (5, '{:>5d}', NMOL)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_2_1_1(IFORM = None,
                 PAVE = None,
                 TAVE = None,
                 PZ_bot = None,
                 TZ_bot = None,
                 PZ_top = None,
                 TZ_top = None):
    
    notes = (
        (10, '{:>15.7e}' if IFORM == 1 else '{:>10.4f}', PAVE),
        (10, '{:>10.4f}', TAVE),
        (23, None, None),
        (8, '{:>8.3f}', PZ_bot),
        (7, '{:>7.2f}', TZ_bot),
        (7, None, None),
        (8, '{:>8.3f}', PZ_top),
        (7, '{:>7.2f}', TZ_top)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)
        

def record_2_1_2(IFORM = None,
                 WKLs = None,
                 WBROAD = None):
    if WKLs and len(WKLs) != 7:
        raise InputErro('There must be 7 molecular\
        species\' column densities.')
    length = 15 if IFORM == 1 else 10
    fmtspec = '{:>15.7e}' if IFORM == 1 else '{:>10.3e}'
    notes = tuple([(length, fmtspec, wkl)\
                  for wkl in WKLs or 7 * [None]]\
                  + [(length, fmtspec, WBROAD)])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_2_1_3(IFORM = None,
                 NMOL = None,
                 WKLs = None):
    N = NMOL - 7 + 1
    if WKLs and len(WKLs) != N:
        raise InputError('NMOL is {}. There must be \
        {} values in WKLs.'.format(NMOL, N))
    notes = tuple((15, '{:>15.7e}', wkl) if IFORM == 1 \
                  else (10, '{:>10.3e}', wkl) \
                  for wkl in WKLs or N * [None])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_2_1_1to3(NMOL = None,
                    PATH_atmpro = None):
    pass
    

def record_2_2(IXMOLS = None):
    notes = (
        (5, '{:>5d}', IXMOLS),
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)
        

def record_2_2_1(IXMOLS = None, XSNAME = None):
    if IXMOLS and len(XSNAME) != IXMOLS:
        raise InputError('IXMOLS = {}, so there must be \
        {} values in XSNAME.'.format(IXMOLS, IXMOLS))
    notes = tuple((10, '{:>10s}', name) for name in XSNAME)
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)
        

def record_2_2_2(IFRMX = None):
    notes = (
        (1, None, None),
        (1, '{:d}', IFRMX)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_2_2_3():
    return ''


def record_2_2_4(IFRMX = None,
                 XAMNT = None):
    if XAMNT and len(XAMNT) != 7:
        raise InputError('XAMNT must have length 7')
    notes = tuple(
        (15, '{:15.7e}', x) if IFRMX == 1 \
        else (10, '{:10.3e}', x) \
        for x in XAMNT or 7 * [None])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)
    
    
def record_2_2_3to5(IXMOLS = None,
                    PATH_atmpro = None):
    pass




def record_3_1(MODEL = None,
               IBMAX = None,
               NOPRNT = None,
               NMOL = None,
               IPUNCH = None,
               MUNITS = None,
               RE = None,
               CO2MX = None,
               REF_LAT = None):
    notes = (
        (5, '{:>5d}', MODEL),
        (5, None, None),
        (5, '{:>5d}', IBMAX),
        (5, None, None),
        (5, '{:>5d}', NOPRNT),
        (5, '{:>5d}', NMOL),
        (5, '{:>5d}', IPUNCH),
        (3, None, None),
        (2, '{:>2d}', MUNITS),
        (10, '{:>10.3f}', RE),
        (20, None, None),
        (10, '{:10.3f}', CO2MX)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)
        

def record_3_2(HBOUND = None,
               HTOA = None):
    notes = (
        (10, '{:>10.3f}', HBOUND),
        (10, '{:>10.3f}', HTOA)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)
        

def record_3_3_A(AVTRAT = None,
                 TDIFF1 = None,
                 TDIFF2 = None,
                 ALTD1 = None,
                 ALTD2 = None):
    notes = tuple((10, '{:10.3f}', value) \
                  for value in [AVTRAT, TDIFF1, TDIFF2, ALTD1, ALTD2])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)    


def record_3_3_B(IBMAX = None,
                 PATH_atmpro = None):
    Nrow, fmtspec = 8, '{:>10.3f}'
    with pd.get_store(PATH_atmpro) as store:
        atmpro = store['atmpro']
    if IBMAX < 0:
        name = 'pressure'
    elif IBMAX > 0:
        name = 'altitude'
    else:
        raise ValueError('record_3_3_B is not applicable for IMBAX = 0')
    totdata = atmpro[name][::-1][: abs(IBMAX)]
    notes_rows = (
        ((Nrow, fmtspec, value) for value in row) \
        for row in itertools.zip_longest(*(Nrow * [iter(totdata)]))
        )
    records_rows = (''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes) \
                   for notes in notes_rows)
    return '\n'.join(records_rows)


def record_3_4(IMMAX = None,
               HMOD = None):
    notes = (
        (5, '{:>5d}', IMMAX),
        (24, '{:>24s}', HMOD)
        )
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_3_5(NMOL = None,
               ZM = None,
               PM = None,
               TM = None,
               JCHARP = None,
               JCHART = None,
               JCHAR = None):
    notes = tuple([
        (10, '{:>10.3e}', ZM),
        (10, '{:>10.3e}', PM),
        (10, '{:>10.3e}', TM),
        (5, None, None),
        (1, '{:s}', JCHARP),
        (1, '{:s}', JCHART),
        (3, None, None)] + \
                  [(1, '{:s}', jch) for jch in JCHAR or NMOL * [None]])
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)


def record_3_6(NMOL = None,
               VMOL = None):
    if VMOL.shape and len(VMOL) != NMOL:
        raise InputError('NMOL = {}. \
        VMOL must have {} values'.format(NMOL, NMOL))
    notes = tuple((10, '{:>10.3e}', value) for value in VMOL)
    return ''.join(length * ' ' if value == None\
                   else fmtspec.format(value)\
                   for length, fmtspec, value in notes)

        
def record_3_5_to_3_6s(NMOL = None,
                       IMMAX = None,
                       PATH_atmpro = None):
    with pd.get_store(PATH_atmpro) as store:
        atmpro = store['atmpro'].sort_index(ascending = True)

    lines = collections.deque([])
    for indx in atmpro.index[: abs(IMMAX)]:
        lines.append(
            record_3_5(ZM = atmpro.loc[indx, 'altitude'],
                       PM = atmpro.loc[indx, 'pressure'],
                       TM = atmpro.loc[indx, 'temperature'],
                       JCHARP = 'A',
                       JCHART = 'A',
                       JCHAR = NMOL * ['A'])
            )
        lines.append(
            record_3_6(NMOL = NMOL,
                       VMOL = atmpro.ix[indx, 3:])
            )
    return '\n'.join(lines)


def record_3_7(IXMOLS = None,
               IPRFL = None,
               IXSBIN = None):
    pass


def record_3_8(LAYX = None,
               IZORP = None,
               XTITLE = None):
    pass


def record_3_8_1_to_3_8_Ns(IXMOL = None,
                           LAYX = None,
                           PATH_atmpro = None):
    pass


