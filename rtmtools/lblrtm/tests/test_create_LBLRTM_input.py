import os
import unittest
import create_LBLRTM_input as lblrtminput


'''
Test functions
'''
def test_record_1_2():
    print('Test record_1_2()')
    print(record_1_2(IHIRAC = 1, ILBLF4 = 1, ICNTNM = 1, IAERSL = 0,
                     IEMIT = 1, ISCAN = 3, IFILTR = 0, IPLOT = 0,
                     ITEST = 0, IATM = 1, IMRG = 0, ILAS = 0,
                     IOD = 0, IXSECT = 1, MPTS = 0, NPTS = 0
                     ) == ' HI=1 F4=1 CN=1 AE=0 EM=1 SC=3 FI=0 PL=0 TS=0 AM=1 MG 0 LA=0 OD=0 XS=1    0    0')
    
    print(record_1_2( IHIRAC = 1, ILBLF4 = 1, ICNTNM = 1, IAERSL = 0,
                      IEMIT = 1, ISCAN = 3, IFILTR = 0, IPLOT = 0,
                      ITEST = 0, IATM = 1, IMRG = 0, ILAS = 0,
                      IOD = 0, IXSECT = 1, MPTS = 0, NPTS = 0) == ' HI=1 F4=1 CN=1 AE=0 EM=1 SC=3 FI=0 PL=0 TS=0 AM=1 MG 0 LA=0 OD=0 XS=1    0    0')

    
    
def test_record_1_3():
    print('Test record_1_3()')
    print(record_1_3() == 105 * ' ')
    print(record_1_3(DPTMIN = 0.0002, V1 = 8.0000, SAMPLE = 0.0,
                     DPTFAC = 0.001, DVSET = 0.0, ALFAL0 = 0.0,
                     AVMASS = 0.0, ILNFLG = 0, V2 = 2002.0000) == '    8.0000 2002.0000       0.0       0.0       0.0       0.0    0.0002     0.001    0                     ')
    print(record_1_3(DPTMIN = 0.0002, V1 = 8.0000, SAMPLE = 0.0,
                     DPTFAC = 0.001, DVSET = 0.0, ALFAL0 = 0.0,
                     AVMASS = 0.0, ILNFLG = 0, V2 = 2002.0000))
    print('    8.0000 2002.0000       0.0       0.0       0.0       0.0    0.0002     0.001    0                    ')
      

def test_record_1_4():
    print('Test record_1_4()')
    print(record_1_4() == 75 * ' ')
    print(record_1_4(TBOUND = 288.20, SREMIS1 = 1.0) == ' 288.20   1.0                                                              ')
    print(record_1_4(TBOUND = 288.20, SREMIS1 = 1.0))
    print(' 288.20   1.0                                                              ')
    print(record_1_4(TBOUND = 293.3, SREMIS1 = -1.000, SRREFL1 = -1.000) == '293.3         -1.000                        -1.000                         ')
    print(record_1_4(TBOUND = 293.3, SREMIS1 = -1.000, SRREFL1 = -1.000))
    print('293.3         -1.000                        -1.000                         ')


def test_record_1_6a():
    print('Test record_1_6a()')
    print(record_1_6a() == 60 * ' ')
    print(record_1_6a(PTHODL = 'ODdeflt_', LAYTOT = 42) == 'ODdeflt_                                                  42')

    
    
def test_record_3_1():
    print('Test record_3_1()')
    print(record_3_1() == (7 * 5 + 2 + 1 + 2 + 5 * 10) * ' ')
    print(record_3_1(MODEL = 0, ITYPE = 2, IBMAX = 43, ZERO = 1,
                     NOPRNT = 0, NMOL = 7, IPUNCH = 1, IFXTYP = 0,
                     MUNITS = 0, RE = 6356.910, HSPACE = 0.000, VBAR = 0.000,
                     REF_LAT = '') == '    0    2   43    1    0    7    1 0  0  6356.910     0.000     0.000                    ')

def test_record_3_2():
    print('Test record_3_2()')
    print(record_3_2() == 70 * ' ')
    print(record_3_2(ANGLE = 180., H1 = 64.64, H2 = 0) == '   64.6400    0.0000  180.0000                                        ')



def test_record_3_3B():
    print('Test record_3_3B()')
    print(record_3_3B(0.000, 0.468, 1.038, 1.490, 2.051, 3.048, 4.027, 5.033,
                     6.023, 6.962, 7.861, 8.865, 9.412, 10.026, 10.654, 11.319,
                     12.062, 12.911, 13.865, 14.277, 15.238, 16.356, 17.037, 17.758,
                     18.555, 19.536, 19.970) == '     0.000     0.468     1.038     1.490     2.051     3.048     4.027     5.033\n     6.023     6.962     7.861     8.865     9.412    10.026    10.654    11.319\n    12.062    12.911    13.865    14.277    15.238    16.356    17.037    17.758\n    18.555    19.536    19.970')
    print(record_3_3B(0.000, 0.468, 1.038, 1.490, 2.051, 3.048, 4.027, 5.033,
                     6.023, 6.962, 7.861, 8.865, 9.412, 10.026, 10.654, 11.319,
                     12.062, 12.911, 13.865, 14.277, 15.238, 16.356, 17.037, 17.758,
                     18.555, 19.536, 19.970))

def test_record_3_4():
    print('Test record_3_4()')
    print(record_3_4(IMMAX = 97, HMOD = 'INPUT FOR CAMEX') == '   97         INPUT FOR CAMEX')
    print(record_3_4(IMMAX = 97, HMOD = 'INPUT FOR CAMEX'))
    

def test_record_3_5():
    print('Test record_3_5()')
    print(record_3_5() == 79 * ' ')
    print(record_3_5(ZM = 0.000, PM = 1013.250, TM = 288.200,
                     JCHARP = 'A', JCHART = 'A', JLONG = '',
                     JCHAR = 'AAAAAAA') == '     0.000  1013.250   288.200     AA   AAAAAAA                                ')
    print(record_3_5(ZM = 0.000, PM = 1018.000, TM = 291.950, JCHARP = 'A',
                     JCHART = 'A', JLONG = 'L',
                     JCHAR = 'AAAAAAA') == '     0.000  1018.000   291.950     AA L AAAAAAA                                ')
    

def test_record_3_6():
    print('Test record_3_6()')
    print(record_3_6('', 7.7400e+03, 3.6000e+02, 2.6600e-02,
                     3.2000e-01, 1.5000e-01, 1.7000e+00, 2.0900e+05) == '7.7400e+033.6000e+022.6600e-023.2000e-011.5000e-011.7000e+002.0900e+05')
    print(record_3_6('L', 9.07429980e+03, 3.53840000e+02, 4.10549988e-02,
                     3.19999993e-01, 1.45940006e-01, 1.70000005e+00, 2.09000000e+05) == ' 9.07429980e+03 3.53840000e+02 4.10549988e-02 3.19999993e-01 1.45940006e-01 1.70000005e+00 2.09000000e+05')


def test_record_6():
    print('Test record_6()')
    print(record_6() == 80 * ' ')
    print(record_6(HWHM = 0.25, V1 = 9.75, V2 = 2000.25, JEMIT = 1,
                   JFN = 0, NNFILE = 62, NPTS = 00) == ' 0.25        9.75    2000.25      1    0                                 62   00')
    print(record_6(HWHM = 0.25, V1 = 9.75, V2 = 2000.25, JEMIT = 1, JFN = 0, NNFILE = 62, NPTS = 00))
    print(' 0.25        9.75    2000.25      1    0                                 62   00')


def test_record_6_1():
    print('Test record_6_1()')
    print(record_6_1() == 10 * ' ')
    print(record_6_1(DIRCOS = 0.59053314) == '0.59053314')





class IN_RADSUM_record_1(unittest.TestCase):

    known_values = (
        (
        {'V1': 10.0, 'V2': 2000.,
         'OUTINRAT': 3980, 'NANG': 3, 'NLEV': 43,
         'TBND': 288.2, 'IQUAD': 0},
        '      10.0    2000.0 3980    3   43  288.20    0'),
        )
    

    def test_known_values(self):
        func = lblrtminput.IN_RADSUM_record_1
        for arg, ans in self.known_values:
            weget = func(**arg)
            self.assertEqual(weget, ans)



if __name__ == '__main__':
    unittest.main()
