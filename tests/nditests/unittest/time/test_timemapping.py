import unittest
import numpy as np
from ndi.time.timemapping import TimeMapping

class TestTimeMapping(unittest.TestCase):

    def test_timemapping_creation(self):
        tm = TimeMapping()
        self.assertIsInstance(tm, TimeMapping)
        self.assertTrue(np.array_equal(tm.mapping, [1, 0]))

        tm2 = TimeMapping([2, 5])
        self.assertTrue(np.array_equal(tm2.mapping, [2, 5]))

    def test_map(self):
        tm = TimeMapping([2, 5])
        self.assertEqual(tm.map(10), 25)

if __name__ == '__main__':
    unittest.main()
