import unittest
from ndi.dataset import Dataset
from ndi.session.dir import Dir as SessionDir
import tempfile
import shutil

class TestBuildDataset(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session_name = 'mysession'
        self.session = SessionDir(self.session_name, self.temp_dir)
        self.dataset_id = 'test_dataset_id'
        self.dataset_name = 'test_dataset'

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_build_dataset(self):
        """
        Tests the dataset build process, mimicking ndi.unittest.dataset.buildDataset.
        """
        ds = Dataset(self.dataset_name)
        self.assertIsInstance(ds, Dataset)
        self.assertEqual(ds.reference(), self.dataset_name)

if __name__ == '__main__':
    unittest.main()
