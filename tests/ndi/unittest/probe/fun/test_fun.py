import unittest
from ndi.probe import fun as probe_fun

class TestProbeFun(unittest.TestCase):

    def test_init_probe_type_map(self):
        """
        Tests the initialization of the probe type map.
        """
        probe_type_map = probe_fun.init_probe_type_map()
        self.assertIsInstance(probe_type_map, dict)
        self.assertIn('n-trode', probe_type_map)
        self.assertEqual(probe_type_map['n-trode'], 'ndi.probe.timeseries.mfdaq')

    def test_get_probe_type_map(self):
        """
        Tests the retrieval of the probe type map.
        """
        # Ensure the global cache is initially empty
        probe_fun._cached_probe_type_map = None

        # First call should initialize and cache the map
        probe_type_map1 = probe_fun.get_probe_type_map()
        self.assertIsInstance(probe_type_map1, dict)
        self.assertIsNotNone(probe_fun._cached_probe_type_map)

        # Second call should return the cached map
        probe_type_map2 = probe_fun.get_probe_type_map()
        self.assertIs(probe_type_map1, probe_type_map2)

if __name__ == '__main__':
    unittest.main()
