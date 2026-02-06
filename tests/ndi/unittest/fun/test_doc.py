import unittest
from unittest.mock import MagicMock
from ndi.fun.doc import diff, get_doc_types, all_types

class TestDoc(unittest.TestCase):
    def test_diff(self):
        doc1 = MagicMock()
        doc1.document_properties = {
            'base': {'session_id': 's1', 'id': 'd1'},
            'param': 1,
            'depends_on': [{'name': 'dep1', 'value': 'v1'}]
        }

        doc2 = MagicMock()
        doc2.document_properties = {
            'base': {'session_id': 's2', 'id': 'd1'}, # Same ID
            'param': 1,
            'depends_on': [{'name': 'dep1', 'value': 'v1'}]
        }

        # Should be equal (session_id ignored by default, order independent deps)
        eq, report = diff(doc1, doc2)
        self.assertTrue(eq, f"Report: {report}")
        self.assertFalse(report['mismatch'])

        # Unequal param
        doc2.document_properties['param'] = 2
        eq, report = diff(doc1, doc2)
        self.assertFalse(eq)
        self.assertTrue(report['mismatch'])

        # Unequal ID (if not ignored)
        doc2.document_properties['param'] = 1 # Reset param
        doc2.document_properties['base']['id'] = 'd2'
        eq, report = diff(doc1, doc2)
        self.assertFalse(eq)

    def test_get_doc_types(self):
        session = MagicMock()
        doc1 = MagicMock()
        doc1.doc_class.return_value = 'TypeA'
        doc2 = MagicMock()
        doc2.doc_class.return_value = 'TypeB'
        doc3 = MagicMock()
        doc3.doc_class.return_value = 'TypeA'

        session.database_search.return_value = [doc1, doc2, doc3]

        types, counts = get_doc_types(session)
        self.assertEqual(types, ['TypeA', 'TypeB'])
        self.assertEqual(counts, [2, 1])

    def test_all_types(self):
        # Smoke test as it accesses file system
        types = all_types()
        self.assertIsInstance(types, list)

if __name__ == '__main__':
    unittest.main()
