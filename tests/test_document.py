import unittest
from unittest.mock import patch
from ndi.document import Document

class TestDocument(unittest.TestCase):

    @patch('ndi.document.Document._read_blank_definition')
    def test_document_creation(self, mock_read_blank_definition):
        mock_read_blank_definition.return_value = {
            'base': {
                'id': '',
                'datestamp': '',
                'session_id': ''
            },
            'document_class': {
                'class_name': 'test_document',
                'superclasses': []
            }
        }

        doc = Document('test_document', **{'base.name': 'my_doc'})
        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.document_properties['base']['name'], 'my_doc')
        self.assertIsNotNone(doc.document_properties['base']['id'])

    @patch('ndi.document.Document._read_blank_definition')
    def test_set_session_id(self, mock_read_blank_definition):
        mock_read_blank_definition.return_value = {
            'base': {
                'id': '',
                'datestamp': '',
                'session_id': ''
            },
            'document_class': {
                'class_name': 'test_document',
                'superclasses': []
            }
        }

        doc = Document('test_document')
        doc.set_session_id('test_session')
        self.assertEqual(doc.document_properties['base']['session_id'], 'test_session')

if __name__ == '__main__':
    unittest.main()
