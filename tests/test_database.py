import unittest
from unittest.mock import Mock
from ndi.database import Database
from ndi.database.document import Document
from ndi.database.binarydoc import BinaryDoc

class MockDatabase(Database):
    def add(self, doc, **kwargs): pass
    def read(self, doc_id): pass
    def remove(self, doc_id): pass
    def search(self, search_parameters): pass
    def alldocids(self): return []

class MockBinaryDoc(BinaryDoc):
    def fopen(self): pass
    def fseek(self, location, reference): pass
    def ftell(self): pass
    def feof(self): pass
    def fwrite(self, data, precision, skip): pass
    def fread(self, count, precision, skip): pass
    def fclose(self): pass

class TestDatabase(unittest.TestCase):

    def test_database_creation(self):
        db = MockDatabase('/fake/path', 'ref1')
        self.assertIsInstance(db, Database)

    def test_document_creation(self):
        doc = Document('base')
        self.assertIsInstance(doc, Document)
        self.assertIsNotNone(doc.id())

    def test_binarydoc_creation(self):
        bin_doc = MockBinaryDoc()
        self.assertIsInstance(bin_doc, BinaryDoc)

if __name__ == '__main__':
    unittest.main()
