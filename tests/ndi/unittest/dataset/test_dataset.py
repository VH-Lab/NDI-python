import unittest
from unittest.mock import Mock, patch
from ndi.dataset import Dataset
from ndi.dataset.dir import Dir as DatasetDir

class TestDataset(unittest.TestCase):

    def test_create_dataset(self):
        """
        Tests the creation of a Dataset object.
        """
        dataset = Dataset('my_dataset')
        self.assertIsInstance(dataset, Dataset)
        self.assertEqual(dataset.reference(), 'my_dataset')

    @patch('ndi.session.dir.Dir')
    def test_create_dataset_dir(self, mock_session_dir):
        """
        Tests the creation of a DatasetDir object.
        """
        # Mock the session.dir object
        mock_session_instance = Mock()
        mock_session_instance.path = '/fake/path'
        mock_session_dir.return_value = mock_session_instance

        # Test creating a dataset with a path
        dataset_dir = DatasetDir('/fake/path')
        self.assertIsInstance(dataset_dir, DatasetDir)
        self.assertEqual(dataset_dir.path, '/fake/path')

        # Test creating a dataset with a reference and path
        dataset_dir_with_ref = DatasetDir('my_dataset', '/another/fake/path')
        self.assertIsInstance(dataset_dir_with_ref, DatasetDir)
        self.assertEqual(dataset_dir_with_ref.path, '/another/fake/path')


if __name__ == '__main__':
    unittest.main()
