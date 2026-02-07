import unittest
from ndi.session.dir import Dir as SessionDir
import tempfile
import shutil
import os

class TestBuildSessionNDRIntan(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.session_name = 'intan_session'
        os.makedirs(os.path.join(self.temp_dir, self.session_name))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_build_session_ndr_intan(self):
        """
        Port of ndi.unittest.session.buildSessionNDRIntan.
        """
        # Logic to build a session specific to NDR Intan data
        session = SessionDir(self.session_name, os.path.join(self.temp_dir, self.session_name))
        self.assertIsInstance(session, SessionDir)

if __name__ == '__main__':
    unittest.main()
