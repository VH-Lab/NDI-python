import unittest
from ndi.query import Query

class TestQuery(unittest.TestCase):

    def test_query_creation(self):
        q = Query('test.field', 'exact_string', 'test_value', '')
        self.assertIsInstance(q, Query)
        self.assertEqual(q.search_structure['field'], 'test.field')

if __name__ == '__main__':
    unittest.main()
