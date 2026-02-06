import unittest
from unittest.mock import Mock
from ndi.database import Database
from ndi.database.document import Document
from ndi.database.binarydoc import BinaryDoc

class MockDatabase(Database):
    def do_add(self, ndi_document_obj, add_parameters): pass
    def do_read(self, ndi_document_id): pass
    def do_remove(self, ndi_document_id): pass
    def do_search(self, searchoptions, searchparams): pass
    def do_openbinarydoc(self, ndi_document_id): pass
    def check_exist_binarydoc(self, ndi_document_id): pass
    def do_closebinarydoc(self, ndi_binarydoc_obj): pass
    def do_open_database(self): pass

class MockBinaryDoc(BinaryDoc):
    def __init__(self): pass
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
