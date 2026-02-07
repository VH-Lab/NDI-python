import unittest
import os
import shutil
import tempfile
from ndi.session.dir import Dir as SessionDir
from ndi.file import Navigator

class TestFileNavigator(unittest.TestCase):

    def setUp(self):
        """
        Set up the test environment.
        """
        self.temp_dir = tempfile.mkdtemp()
        self.create_folder_structure(3)
        self.create_folder_structure_with_files(3, 2, 'dummy', ['.ext'])
        self.create_folder_structure_with_files(3, 2, 'myfile', ['.ext1', '.ext2'])

        self.session = SessionDir('mysession', self.temp_dir)
        self.file_navigator = Navigator(self.session, fileparameters={'filematch': ['myfile_#.ext1', 'myfile_#.ext2']})

    def tearDown(self):
        """
        Clean up the test environment.
        """
        shutil.rmtree(self.temp_dir)

    def create_folder_structure(self, num_subdirs):
        """
        Creates a folder structure for testing.
        """
        for i in range(1, num_subdirs + 1):
            subdir_name = os.path.join(self.temp_dir, f'mysubdir{i}')
            if not os.path.exists(subdir_name):
                os.makedirs(subdir_name)

    def create_folder_structure_with_files(self, num_subdirs, num_files, file_base_name, file_extensions):
        """
        Creates a folder structure with dummy files for testing.
        """
        for i in range(1, num_subdirs + 1):
            subdir_name = os.path.join(self.temp_dir, f'mysubdir{i}')
            for j in range(1, num_files + 1):
                for ext in file_extensions:
                    file_name = f'{file_base_name}_{j}{ext}'
                    file_path = os.path.join(subdir_name, file_name)
                    with open(file_path, 'w') as f:
                        pass

    @unittest.skip("Not implemented")
    def test_number_of_epochs(self):
        """
        Tests that the number of epochs is correct.
        """
        self.assertEqual(self.file_navigator.numepochs(), 6)

    @unittest.skip("Not implemented")
    def test_epoch_files(self):
        """
        Tests that epoch files can be retrieved correctly.
        """
        files = self.file_navigator.getepochfiles(2)
        self.assertEqual(len(files), 2)
        self.assertTrue(files[0].endswith('myfile_2.ext1'))
        self.assertTrue(files[1].endswith('myfile_2.ext2'))

    @unittest.skip("Not implemented")
    def test_epoch_table_entries(self):
        """
        Tests that the epoch table is built correctly.
        """
        et = self.file_navigator.epochtable()
        self.assertEqual(len(et), 6)
        self.assertEqual(et[0]['epoch_number'], 1)
        self.assertEqual(et[0]['epoch_id'], 'epoch_1')
        self.assertEqual(len(et[0]['underlying_epochs']['underlying']), 2)


if __name__ == '__main__':
    unittest.main()
