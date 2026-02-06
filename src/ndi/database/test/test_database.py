import unittest
from ndi.database.document import Document

class TestDatabase(unittest.TestCase):
    def test_document_instantiation(self):
        doc = Document('base', my_field='my_value')
        self.assertIsNotNone(doc)
        self.assertEqual(doc.document_properties['my_field'], 'my_value')
        self.assertIn('id', doc.document_properties['base'])

    def test_document_dependency(self):
        doc = Document('base')
        doc.set_dependency_value('my_dependency', 'dependency_value', error_if_not_found=False)
        value = doc.dependency_value('my_dependency')
        self.assertEqual(value, 'dependency_value')

if __name__ == '__main__':
    unittest.main()
