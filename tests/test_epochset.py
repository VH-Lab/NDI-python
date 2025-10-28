import unittest
from ndi.epoch.epochset import EpochSet

class TestEpochSet(unittest.TestCase):

    def test_epochset_creation(self):
        es = EpochSet()
        self.assertIsInstance(es, EpochSet)

    def test_num_epochs(self):
        es = EpochSet()
        self.assertEqual(es.num_epochs(), 0)

if __name__ == '__main__':
    unittest.main()
