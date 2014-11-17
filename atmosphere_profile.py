'''
Most things to do with atmospheric profiles 
'''
import os
import sys
import itertools
import collections
import numpy as np
import scipy as sp
import scipy.io as spio
import pandas as pd





def ERAIN_to_DataFrame(readfrom = 'erain.nc'):
    '''
    Get some atmosphere profile data from a
    ERAIN netcdf file
    '''
    with spio.netcdf_file(readfrom,\
                          mode = 'r', mmap = False) as file:
        plev_gb = file.variables['plev']
        t = file.variables['t']
        sp = file.variables['sp']
        play_gb = file.variables['play']
        q = file.variables['q']
        o3 = file.variables['o3']
        skt = file.variables['skt']
        sstk = file.variables['sstk']

    # some of these variabels have a dimension with
    # length 1, so we'll just access it to get rid
    # of this d

    # just do the first column for now
    ilon, ilat = 0, 0

    # determine how low the lowest layers should be
    # using local surface pressure sp

    sp_local = 1e-2 * sp.data[:, ilon, ilat] # convert Pa to hPa
    
    if sp_local >= play_gb.data[-1]:
        nlayer = play_gb.shape[0]
    else:
        nlayer = np.where(\
            play_gb.data - sp_local < 0)[-1] + 1

    plevel = np.concatenate(
        (
        plev_gb.data[:, : nlayer, ilon, ilat],
        [sp_local]
        ),
        axis = 1)
    tlayer = t.data[:, : nlayer, ilon, ilat]
    wlayer = q.data[:, : nlayer, ilon, ilat]
    clayer = 370e-6 * np.ones(tlayer.shape)
    olayer = o3.data[:, : nlayer, ilon, ilat]
    qlayer = .32e-6 * np.ones(tlayer.shape)
    rlayer = 1.75e-6 * np.ones(tlayer.shape)
    tsfc = skt.data[:, ilon, ilat]

    # convert units of N2O and CH4 from [l/l] to [g/g]
    qlayer *= 44 / 28.97
    rlayer *= 16 / 28.97

    names = ['plevel', 'tlayer', 'wlayer', 'clayer',\
             'olayer', 'qlayer', 'rlayer']
    
    profiles = [plevel, tlayer, wlayer, clayer,\
                olayer, qlayer, rlayer]
    profiles = [np.squeeze(profile) for profile in profiles]
    profiles = [profile.astype('f4') if profile.dtype != 'f4'\
                else profile for profile in profiles]
    profiles = (pd.Series(profile[:: -1],\
                          index = range(profile.shape[0]),\
                          name = name)\
                for name, profile in zip(names, profiles))
    print('tsfc = ', tsfc)
    return pd.concat(profiles, axis = 1).sort_index(ascending = False)



        

        
    

    
    
        
        
    
