




def wavenumber_bands():
    '''
    Returns wavenumber bands used by RRTMG-SW
    Units: cm-1
    '''
    wavenum1 = [10., 350., 500., 630., 700., 820., 
                 980., 1080., 1180., 1390., 1480., 1800.,  
                 2080., 2250., 2390., 2600.]
    wavenum2 = [350.,  500.,  630.,  700.,  820.,  980.,  
                1080., 1180., 1390., 1480., 1800., 2080.,  
                2250., 2390., 2600., 3250.]
    return {k + 1: [(low, high)] for k, (low, high) in enumerate(zip(wavenum1, wavenum2))}
