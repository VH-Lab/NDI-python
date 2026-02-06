import unittest
from ndi.subject import Subject
from unittest.mock import patch

class TestSubject(unittest.TestCase):

    def test_subject_creation(self):
        s = Subject('test@test.com', 'a test subject')
        self.assertIsInstance(s, Subject)
        self.assertEqual(s.local_identifier, 'test@test.com')

    @patch('ndi.subject.Document')
    @patch('ndi.subject.Session')
    def test_new_document(self, mock_session, mock_document):
        mock_session.empty_id.return_value = '00000000-0000-0000-0000-000000000000'
        s = Subject('test@test.com', 'a test subject')
        doc = s.new_document()
        mock_document.assert_called_with('subject',
            **{
                'subject.local_identifier': 'test@test.com',
                'subject.description': 'a test subject',
                'base.id': s.id(),
                'base.name': 'test@test.com',
                'base.session_id': '00000000-0000-0000-0000-000000000000'
            }
        )

if __name__ == '__main__':
    unittest.main()
