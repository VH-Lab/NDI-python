import unittest
from ndi.dataset import Dataset
import tempfile
import shutil

class TestDatasetConstructor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_dataset_constructor(self):
        """
        Port of ndi.unittest.dataset.testDatasetConstructor.
        """
        ds = Dataset('ds_constructor_ref')
        self.assertIsNotNone(ds)
        self.assertEqual(ds.reference(), 'ds_constructor_ref')

if __name__ == '__main__':
    unittest.main()
