import os
import sys
import create_LBLRTM_input as lblrtmin




def filepath_aerlinefile():
    return '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/aer_v_3.2/line_file/aer_v_3.2'


def filepath_lnfl():
    return '/nuwa_cluster/home/jackyu/line_by_line/aerlbl_v12.2_package/lnfl/lnfl_v2.6_linux_intel_sgl'


def lnfl(XID = '',
         VMIN = 0., VMAX = 3000.,
         MIND1 = 39 * '0', HOLIND1 = '',
         saveas = 'TAPE3'):
    '''
    Writes TAPE5 for LNFL, runs it and write TAPE3 to disk
    '''
    [os.remove(file)
     for file in ('TAPE1', 'TAPE3', 'TAPE5', 'lnfl') if os.path.isfile(file)]

    lblrtmin.write_LNFL_TAPE5(XID = XID,
                              VMIN = VMIN, VMAX = VMAX,
                              MIND1 = MIND1, HOLIND1 = HOLIND1)
    
    os.symlink(filepath_aerlinefile(), 'TAPE1')
    os.symlink(filepath_lnfl(), 'lnfl')
    
    print('Running LNFL')
    os.system('lnfl')

    os.rename('TAPE3', saveas)
    
    



