

def wavenumber_bands():
    d = {}
    d[1] = [(0, 340),]          #  h2o
    d[2] = [(340, 540),]        #  h2o
    d[3] = [(540, 800),]        #  h2o,cont,co2
    d[4] = [(800, 980),]        #  h2o,cont,  co2,f11,f12,f22
    d[5] = [(980, 1100),]       #  h2o,cont,o3
                                #  co2,f11
    d[6] = [(1100, 1215),]      #    h2o,cont
#        c                              n2o,ch4,f12,f22
    d[7] = [(1215, 1380),]      #  h2o,cont
#        c                              n2o,ch4
    d[8] = [(1380, 1900),]      #    h2o
    d[9] = [(1900, 3000),]      #    h2o
#        c
#        c In addition, a narrow band in the 17 micrometer region (Band 10) is added
#        c    to compute flux reduction due to n2o
#        c
    d[10] = [(540, 620)]       # h2o,cont,co2,n2o
    return d
