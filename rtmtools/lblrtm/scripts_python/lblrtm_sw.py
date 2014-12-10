
'''
Calculation ID. Write something to identify this calculation.
'''
CXID = 'LBLRTM solar test run mls 71 levels'


'''
Starting wavenumber
'''
V1 = 20000


'''
Ending waveumber
'''
V2 = 22000


'''
Solar zenith angle
'''
ANGLE = 0.


'''
Concentration of molecules in the atmosphere
H2O --- H2O concentration [g/g] (None if default to Chou\'s mls75pro)
CO2 --- CO2 concentration [ml/ml] 
O3  --- O3 concentration [g/g] (None if default to Chou\'s mls75pro)
N2O --- N2O concentration [g/g]
CO --- CO concentration [g/g]
CH4 --- CH4 concentration [g/g]
O2 --- O2 concentration [g/g]
'''
H2O = None
CO2 = 0.
O3  = None
N2O = 0.
CO  = 0.
CH4 = 0.
O2  = 0.



'''
Path to Chou\'s mls75pro atmosphere profile (this should be the formatted\
Fortran file)
'''
path_mls75pro = ''








if __name__ == '__main__':
    import os
    import scipy.io
    import itertools
    import collections
    import pandas as pd
    import numpy as np
    import rtmtools.lblrtm.create_LBLRTM_input as lblrtmin
    import rtmtools.lblrtm.aerutils as aerutils

    # Get atmpro DataFrame
    lblrtmin.atmopro_mls75pro(outputfilename = 'mls75pro.dat',
                              lev0_temp = 294.0,
                              H2O = H2O,
                              CO2 = CO2,
                              O3  = O3,
                              N2O = N2O,
                              CO  = CO,
                              CH4 = CH4,
                              O2  = O2,
                              up_to_level = 71)

    df_atmpro = aerutils.atmpro_txtfile_to_pandasDataFrame(\
        readfrom = 'mls75pro.dat')

    # run LBLRTM for increasing H1 (in pressure)
    H2 = df_atmpro['pressure'][df_atmpro.index[0]]
    dfs = collections.deque([])
    
    for indx in df_atmpro.index[1: 3]:
        H1 = df_atmpro['pressure'][indx]
        print('H1 = ', H1, 'mb')

        # write TAPE5
        tape5 = lblrtmin.write_solar_downwelling_TAPE5(
            CXID = CXID,
            atmpro = df_atmpro,
            ICNTNM = 0,
            V1 = V1, V2 = V2,
            MODEL = 0,
            H1 = H1, H2 = H2, ANGLE = ANGLE,
            )
        with open('TAPE5', mode = 'w', encoding = 'utf-8') as f:
            f.write(tape5)

        # run LBLRTM
        os.system('./lblrtm_dbl')

        # read TAPE13 for radiance
        records = aerutils.read_lblrtm_spectral_output_files(readfrom = 'TAPE13')

        # integrate radiance over each 11 cm-1 band 
        records = itertools.islice(records, 1, len(records))
        bands = itertools.zip_longest(*(2 * [records]))
        bands = ((wvnums[0], wvnums[1], radiance.sum())\
                 for wvnums, radiance in bands)
        V1s, V2s, rads = itertools.zip_longest(*bands)
        df_rad = pd.DataFrame(data = np.array(rads),
                              index = [np.array(V1s), np.array(V2s)],
                              columns = [H1])

        # append integrated radiance to those at other H1 (pressures)
        dfs.append(df_rad)

    # construct DataFrame (wavenumber bands, pressure) of radiances
    df_allrad = pd.concat(list(dfs), axis = 1)
    df_allrad.index.names = ['V1', 'V2']
    df_allrad.columns.names = ['pressure']

    # change radiance to flux (using instructions by Karen)
    df_allrad *= 6.8e-1 * np.cos(np.deg2rad(ANGLE))
    
    print(df_allrad.shape)
    print(df_allrad.columns)
    print(df_allrad.index)
    print(df_allrad.head())
    print(df_allrad.tail())
    
    


