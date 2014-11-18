import os
import sys
import re
import shutil
import argparse
import create_LBLRTM_input as lblrtmin
import aer_flux_calculation as aerfluxcalc
import plotting 




'''
Atmospheric profile
'''
filepath_atmpro = 'atmopro.dat'
lblrtmin.atmopro_mls75pro(outputfilename = filepath_atmpro,
                          lev0_temp = 294.,
                          H2O = None,
                          O3 = 0.,
                          CO2 = 0.,
                          up_to_level = 72)


'''
LBLRTM input
'''
CXID = ''
V1, V2 = 25.0, 100.0
TBOUND = 288.20
ICNTNM = 0
JLONG = ''


'''
Added input
'''
DeltaV = 2000.




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean',
                        action = 'store_true',
                        help = 'Cleans up the directory')
    parser.add_argument('--run',
                        action = 'store_true',
                        help = 'Runs the flux calculation')
    
    args = parser.parse_args()

    

    if args.clean:
        p = re.compile(r'(?! .* [.]py$ | OUTPUT_.*$ | TAPE5(_.*)?$ | TAPE6(_.*)?$ )', re.VERBOSE)
        [os.remove(item) for item in os.listdir()
         if p.match(item) and os.path.isfile(item)]

        
    if args.run:
        aerfluxcalc.run(atmpro = filepath_atmpro,
                        CXID = CXID,
                        V1 = V1, V2 = V2,
                        TBOUND = TBOUND,
                        ICNTNM = ICNTNM, JLONG = JLONG, 
                        DeltaV = DeltaV)
        


    


