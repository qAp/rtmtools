


def wavenumber_bands():
    '''
    Returns wavenumber bands used by RRTMG-SW
    Units: cm-1
    '''
    wavenum1 = [2600., 3250., 4000., 4650., 5150., 6150., 7700., 
                8050.,12850.,16000.,22650.,29000.,38000.,  820.]
    wavenum2 = [3250., 4000., 4650., 5150., 6150., 7700., 8050., 
                12850.,16000.,22650.,29000.,38000.,50000., 2600.]

    return {k + 1: [(low, high)] for k, (low, high) in enumerate(zip(wavenum1, wavenum2))}

