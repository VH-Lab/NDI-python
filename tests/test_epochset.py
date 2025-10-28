import unittest
from ndi.epoch.epochset import Param

class TestEpochSet(unittest.TestCase):

    def test_epochset_creation(self):
        es = Param()
        self.assertIsInstance(es, Param)

    def test_num_epochs(self):
        es = Param()
        self.assertEqual(es.numepochs(), 0)

if __name__ == '__main__':
    unittest.main()
