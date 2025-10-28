import unittest
from ndi.documentservice import DocumentService
from ndi.document import Document

class TestDocumentService(unittest.TestCase):

    def test_new_document(self):
        ds = DocumentService()
        doc = ds.new_document('base')
        self.assertIsInstance(doc, Document)

if __name__ == '__main__':
    unittest.main()
