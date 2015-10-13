import os
import sys
import numpy as np
import itertools
import collections
import fileinput
import rtmtools.lblrtm.create_LBLRTM_input as lblrtmin


def filepath_TAPE3():
    '''
    Returns the absolute path of TAPE3 to be used in LBLRTM
    '''
    return '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/lnfl/myrun_/TAPE3'

def filepath_IN_RADSUM():
    return '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/radsum/run_examples/IN_RADSUM'

def filepath_lblrtm():
    '''
    Returns the absolute path of lblrtm (the executable)
    '''
    return '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/lblrtm/lblrtm_v12.2_linux_intel_dbl'

def filepath_radsum():
    return '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/radsum/radsum_v2.6_linux_intel_dbl'


def lblrtm(atmpro = 'atmopro.dat',
           CXID = 'Verify RADSUM run_example',
           V1 = 8., V2 = 2002.,
           ICNTNM = 1, JLONG = '', TBOUND = 288.2):
    '''
    Runs the LBLRTM part of flux calculation
    '''
    [os.remove(file)
     for file in ('TAPE3', 'TAPE5', 'lblrtm') if os.path.isfile(file)]
    lblrtmin.write_fluxcalc_TAPE5(atmpro = atmpro,
                                  CXID = CXID, 
                                  V1 = V1, V2 = V2,
                                  ICNTNM = ICNTNM,
                                  JLONG = JLONG,
                                  TBOUND = TBOUND)
    os.symlink(filepath_TAPE3(), 'TAPE3')
    os.symlink(filepath_lblrtm(), 'lblrtm')
    print('Running LBLRTM')
    os.system('./lblrtm')


def radsum(atmpro = 'atmopro.dat', V1 = 10., V2 = 2000.,
           OUTINRAT = 3980, NANG = 3):
    '''
    Runs the RADSUM part of the flux calculation: radiance to flux
    '''
    [os.remove(file)
     for file in ('IN_RADSUM', 'radsum') if os.path.isfile(file)]
    lblrtmin.write_IN_RADSUM(atmpro = atmpro,
                             V1 = V1, V2 = V2,
                             OUTINRAT = OUTINRAT, NANG = NANG)
    os.symlink(filepath_radsum(), 'radsum')
    print('Running RADSUM')
    os.system('./radsum')


def run(atmpro = 'atmopro.dat', CXID = 'Verify RADSUM run_example',
        V1 = 8., V2 = 2002., TBOUND = 288.20, ICNTNM = 0, JLONG = '',
        DeltaV = 2000.):
    '''
    Runs LBLRTM and RADSUM given their inputs.  The wavenumber range
    between V1 and V2 is split into sections of length DELTAV
    , with an additional section if there are any wavenumber left.
    DELTAV is limited by AER to be 2020 cm-1.  For each section
    LBLRTM and RADSUM are run.  
    '''
    if DeltaV > 2020:
        raise ValueError('DeltaV must be <= 2020 cm -1')
    
    boundary_Vs = np.append(np.arange(V1, V2, DeltaV), V2)
    V1V2s = itertools.zip_longest(boundary_Vs[:-1], boundary_Vs[1:])
    
    output_radsum_names = collections.deque([])
    for v1, v2 in V1V2s:
        print('V1 = {}, V2 = {}'.format(v1, v2))
        OUTINRAT = int(2 * (v2 - v1))
        lblrtm(atmpro = atmpro,
               CXID = CXID,
               V1 = v1, V2 = v2,
               ICNTNM = ICNTNM, JLONG = JLONG, TBOUND = TBOUND)
        radsum(atmpro = atmpro,
               V1 = v1, V2 = v2,
               OUTINRAT = 2)
        output_radsum_name = ''.join(['OUTPUT_RADSUM', '_V1_{}_V2_{}'.format(v1, v2)])
        os.rename('OUTPUT_RADSUM', output_radsum_name)
        output_radsum_names.append(output_radsum_name)

    with open('OUTPUT_RADSUM', mode = 'w', encoding = 'utf-8') as fout:
        for line in fileinput.input(output_radsum_names):
            fout.write(line)

    [os.remove(file) for file in output_radsum_names]
        
    
        





if __name__ == '__main__':
    pass

