import unittest
from ndi.dataset import Dataset
import tempfile
import shutil

class TestSessionList(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_session_list(self):
        """
        Port of ndi.unittest.dataset.testSessionList.
        """
        ds = Dataset('ds_list_test')
        with self.assertRaises(NotImplementedError):
             ds.session_list()

if __name__ == '__main__':
    unittest.main()
