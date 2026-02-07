import unittest
import pandas as pd
import numpy as np
from ndi.fun.table import vstack

class TestTable(unittest.TestCase):
    def test_vstack(self):
        # Example 1: Basic concatenation
        df1 = pd.DataFrame({'ID': [1, 2], 'Data': ['a', 'b']})
        df2 = pd.DataFrame({'ID': [3, 4], 'Value': [10.5, 20.6]})

        # vstack should align columns
        stacked = vstack([df1, df2])

        self.assertEqual(len(stacked), 4)
        self.assertIn('ID', stacked.columns)
        self.assertIn('Data', stacked.columns)
        self.assertIn('Value', stacked.columns)

        # Check values
        self.assertEqual(stacked.iloc[0]['Data'], 'a')
        self.assertTrue(np.isnan(stacked.iloc[2]['Data']) or stacked.iloc[2]['Data'] is None) # Data is missing for 2nd table
        self.assertTrue(np.isnan(stacked.iloc[0]['Value'])) # Value is missing for 1st table

    def test_vstack_empty(self):
        df1 = pd.DataFrame({'A': [1]})
        res = vstack([df1])
        self.assertEqual(len(res), 1)

        res = vstack([])
        self.assertTrue(res.empty)

if __name__ == '__main__':
    unittest.main()
