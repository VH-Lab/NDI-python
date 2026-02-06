import unittest
from ndi.fun.stimulus_temporal_frequency import stimulus_temporal_frequency

class TestStimulus(unittest.TestCase):
    def test_stimulus_temporal_frequency(self):
        # Case 1: Direct frequency
        params1 = {'tFrequency': 8, 'spatialFreq': 0.1}
        tf1, name1 = stimulus_temporal_frequency(params1)
        self.assertEqual(tf1, 8)
        self.assertEqual(name1, 'tFrequency')

        # Case 2: Another name
        params2 = {'temporalFrequency': 10}
        tf2, name2 = stimulus_temporal_frequency(params2)
        self.assertEqual(tf2, 10)
        self.assertEqual(name2, 'temporalFrequency')

        # Case 3: Period with multiplier
        # t_period -> 1/t_period * refreshRate
        # if t_period=10, refreshRate=60, tf = (1/10)*60 = 6
        params3 = {'t_period': 10, 'refreshRate': 60}
        tf3, name3 = stimulus_temporal_frequency(params3)
        self.assertEqual(tf3, 6.0)
        self.assertEqual(name3, 't_period')

        # Case 4: No match
        params4 = {'contrast': 1.0}
        tf4, name4 = stimulus_temporal_frequency(params4)
        self.assertIsNone(tf4)
        self.assertEqual(name4, '')

if __name__ == '__main__':
    unittest.main()
