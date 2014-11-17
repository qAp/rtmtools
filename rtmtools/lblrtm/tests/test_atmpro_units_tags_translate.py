import unittest
import aerutils


class atmpro_units_tags_translate(unittest.TestCase):

    known_values = (
        {'property': 'pressure', 'units': 'mb', 'unitsin': 'tags',
         'ans': 'A'},
        {'property': 'pressure', 'units': 'atm', 'unitsin': 'tags',
         'ans': 'B'},
        {'property': 'pressure', 'units': 'torr', 'unitsin': 'tags',
         'ans': 'C'},
        {'property': 'pressure', 'units': ['mb'], 'unitsin': 'tags',
         'ans': ('A',)},
        {'property': 'pressure', 'units': ['atm'], 'unitsin': 'tags',
         'ans': ('B',)},
        {'property': 'pressure', 'units': ['torr'], 'unitsin': 'tags',
         'ans': ('C',)},
        {'property': 'pressure', 'units': ('atm', 'torr'), 'unitsin': 'tags',
         'ans': ('B', 'C')},
        {'property': 'pressure', 'units': ['atm', 'C'], 'unitsin': 'tags',
         'ans': ('B', 'C')},
        {'property': 'pressure', 'units': ('atm', 'C', 'A', 'mb'), 'unitsin': 'tags',
         'ans': ('B', 'C', 'A', 'A')},
        {'property': 'pressure', 'units': ('atm', 'C', 'A', 'mb'), 'unitsin': 'units',
         'ans': ('atm', 'torr', 'mb', 'mb')},
        {'property': 'pressure', 'units': ('C', 'C', 'A', 'B'), 'unitsin': 'tags',
         'ans': ('C', 'C', 'A', 'B')},
        {'property': 'temperature', 'units': ('A',), 'unitsin': 'tags',
         'ans': ('A',)},
        {'property': 'temperature', 'units': 'B', 'unitsin': 'tags',
         'ans': 'B'},
        {'property': 'temperature', 'units': 'C', 'unitsin': 'tags',
         'ans': 'B'},
        {'property': 'temperature', 'units': ['B', 'A', 'A', 'A', 'B'], 'unitsin': 'tags',
         'ans': ('B', 'A', 'A', 'A', 'B')},
        {'property': 'temperature', 'units': ['B', 'K', 'K', 'A', 'C'], 'unitsin': 'tags',
         'ans': ('B', 'A', 'A', 'A', 'B')},
        {'property': 'temperature', 'units': ('B', 'K', 'K', 'A', 'C'), 'unitsin': 'units',
         'ans': ('C', 'K', 'K', 'K', 'C')},
        {'property': 'temperature', 'units': ['A'], 'unitsin': 'units',
         'ans': ('K',)},
        {'property': 'molecule', 'units': ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'),
         'unitsin': 'tags',
         'ans': ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I')},
        {'property': 'molecule', 'units': ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'),
         'unitsin': 'units',
         'ans': ('ppmv', 'cm-3', 'gm/kg', 'gm m-3', 'mb', 'dew point temp (K) *H2O only*',
                 'dew point temp (C) *H2O only*',
                 'relative humidity (percent) *H2O only*',
                 'available for user identification')},
        {'property': 'molecule', 'units': ('gm m-3', 'B', 'ppmv', 'A',),
         'unitsin': 'units',
         'ans': ('gm m-3', 'cm-3', 'ppmv', 'ppmv',)},
        {'property': 'molecule', 'units': ('gm m-3', 'B', 'ppmv', 'A',),
         'unitsin': 'tags',
         'ans': ('D', 'B', 'A', 'A',)},
        )


    def test_known_values(self):
        test_func = aerutils.atmpro_units_tags_translate
        for known_value in self.known_values:
            self.assertEqual(test_func(property = known_value['property'],
                                       units = known_value['units'],
                                       unitsin = known_value['unitsin']),
                             known_value['ans'])



if __name__ == '__main__':
    unittest.main()

            
    
