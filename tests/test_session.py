import unittest
import os
import shutil
from ndi.session import Session
from ndi.session.dir import Dir as SessionDir
from ndi.session.mock import Mock as MockSession

class TestSession(unittest.TestCase):

    def test_create_session(self):
        """
        Tests the creation of a Session object.
        """
        session = Session('my_session')
        self.assertIsInstance(session, Session)
        self.assertEqual(session.reference, 'my_session')
        self.assertIsNotNone(session.id())

    def test_create_session_dir(self):
        """
        Tests the creation of a SessionDir object.
        """
        session_dir = SessionDir('my_session', '/fake/path')
        self.assertIsInstance(session_dir, SessionDir)
        self.assertEqual(session_dir.reference, 'my_session')
        self.assertEqual(session_dir.getpath(), '/fake/path')

    def test_create_mock_session(self):
        """
        Tests the creation of a MockSession object.
        """
        mock_session = MockSession()
        self.assertIsInstance(mock_session, MockSession)
        self.assertTrue(os.path.exists(mock_session.getpath()))
        # Clean up the temporary directory
        shutil.rmtree(mock_session.getpath())

if __name__ == '__main__':
    unittest.main()
