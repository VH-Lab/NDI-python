import unittest
from ndi.epoch.epochset import Param

class MockParam(Param):
    def buildepochtable(self):
        return []

class TestEpochSet(unittest.TestCase):

    def test_epochset_creation(self):
        es = MockParam()
        self.assertIsInstance(es, Param)

    def test_num_epochs(self):
        es = MockParam()
        self.assertEqual(es.numepochs(), 0)

if __name__ == '__main__':
    unittest.main()
