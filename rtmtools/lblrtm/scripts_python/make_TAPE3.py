import os
import sys
import re
import argparse
import aer_lnfl
import aerutils


'''
LNFL INPUT
'''

XID = ''

VMIN, VMAX =  ,

saveas = 'TAPE3'


H2O = 1
CO2 = 1
O3 = 1
N2O = 1
CO = 1
CH4 = 1
O2 = 1
NO = 1
SO2 = 1
NO2 = 1
NH3 = 1
HNO3 = 1
OH = 1
HF = 1
HCL = 1
HBR = 1
HI = 1
CLO = 1
OCS = 1
H2CO = 1
HOCL = 1
N2 = 1
HCN = 1
CH3CL = 1
H2O2 = 1
C2H2 = 1
C2H6 = 1
PH3 = 1
COF2 = 1
SF6 = 1
H2S = 1
HCOOH = 1
HO2 = 1
O = 1
CLONO2 = 1
NOplus = 1
HOBR = 1
C2H4 = 1
CH3OH = 1


HOLIND1 = ''


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--clean',
                        action = 'store_true',
                        help = 'Cleans up the directory')
    parser.add_argument('--run',
                        action = 'store_true',
                        help = 'Runs LNFL to get TAPE3')

    args = parser.parse_args()


    if args.clean:
        p = re.compile(r'(?! .*[.]py$ | TAPE7.*$)', re.VERBOSE)
        [os.remove(name) for name in os.listdir()
         if p.match(name) and os.path.isfile(name)]

    if args.run:
        MIND1 = aerutils.atoms_to_MIND1(H2O = H2O, CO2 = CO2, O3 = O3, N2O = N2O, CO = CO,
                                        CH4 = CH4, O2 = O2, NO = NO, SO2 = SO2, NO2 = NO2,
                                        NH3 = NH3, HNO3 = HNO3, OH = OH, HF = HF, HCL = HCL,
                                        HBR = HBR, HI = HI, CLO = CLO, OCS = OCS, H2CO = H2CO,
                                        HOCL = HOCL, N2 = N2, HCN = HCN, CH3CL = CH3CL,
                                        H2O2 = H2O2, C2H2 = C2H2, C2H6 = C2H6, PH3 = PH3,
                                        COF2 = COF2, SF6 = SF6, H2S = H2S, HCOOH = HCOOH,
                                        HO2 = HO2, O = O, CLONO2 = CLONO2, NOplus = NOplus,
                                        HOBR = HOBR, C2H4 = C2H4, CH3OH = CH3OH)
        aer_lnfl.lnfl(XID = XID,
                      MIND1 = MIND1, HOLIND1 = HOLIND1,
                      VMIN = VMIN, VMAX = VMAX,
                      saveas = saveas)

             
    




