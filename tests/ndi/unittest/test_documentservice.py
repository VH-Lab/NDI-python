import unittest
from ndi.documentservice import DocumentService
from ndi.document import Document

class MockDocumentService(DocumentService):
    def search_query(self):
        pass

class TestDocumentService(unittest.TestCase):

    def test_new_document(self):
        ds = MockDocumentService()
        doc = ds.new_document('base')
        self.assertIsInstance(doc, Document)

if __name__ == '__main__':
    unittest.main()
