



def wavenumber_bands():
    '''
    Returns wavenumber bands used by CLIRAD-SW
    Units: cm-1
    '''
    d = {}
    d[1] = [(35088, 44444),]
    d[2] = [(33333, 35088), (44444, 57142),]
    d[3] = [(30770, 33333),]
    d[4] = [(25000, 30770),]
    d[5] = [(14286, 25000),]
    d[6] = [(8200, 14280),]
    d[7] = [(4400, 8200),]
    d[8] = [(1000, 4400)]
    return d
