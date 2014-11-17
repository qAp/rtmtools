import os
import unittest
import numpy as np
import create_LBLRTM_input as lblrtmin





class Test_PT2altitudes(unittest.TestCase):

    def known_values(self):
        return (
            (np.array([997.1111, 925.0000, 850.0000, 775.0000,
                       700.0000, 600.0000, 500.0000, 400.0000,
                       300.0000, 250.0000, 200.0000, 150.0000,
                       100.0000, 70.0000, 50.0000, 30.0000,
                       20.0000, 10.0000, 7.0000, 5.0000,
                       3.0000, 2.0000, 1.0000]),
             np.array([299.6994, 293.3988, 290.0065, 286.4571,
                       281.9596, 275.1101, 267.0511, 256.2152,
                       240.5350, 230.4459, 218.4822, 204.2563,
                       191.5881, 196.9268, 208.6370, 220.8132,
                       227.4005, 234.9305, 238.4037, 243.0651,
                       253.0762, 260.7341, 263.6019]),
             np.array([0, 0.6517, 1.3737, 2.1531,
                       2.9999, 4.2567, 5.7035, 7.4125,
                       9.5042, 10.7610, 12.2272, 14.0072,
                       16.3564, 18.3846, 20.3819, 23.5928,
                       26.2527, 30.9432, 33.4142, 35.7853,
                       39.4948, 42.5440, 47.8635])),
            )

    def test_shape(self):
        '''
        Check that exception is raised if P and T\'s shapes
        are not the same
        '''
        with self.assertRaises(lblrtmin.ShapeMismatchError):
            lblrtmin.PT2altitudes(np.arange(10), np.arange(11))

    def test_conversion(self):
        '''
        Test using known conversion from to_RCEC
        Check up to 3 decimal places
        '''
        for p, t, z in self.known_values():
            self.assertTrue(
                np.testing.assert_array_almost_equal(
                lblrtmin.PT2altitudes(pressure = p,temperature = t),
                z,
                decimal = 3) is None)


if __name__ == '__main__':
    unittest.main()

    
