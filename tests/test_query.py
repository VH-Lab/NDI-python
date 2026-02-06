import unittest
from ndi.query import Query

class TestQuery(unittest.TestCase):

    def test_query_creation(self):
        q = Query('test.field', 'exact_string', 'test_value', '')
        self.assertIsInstance(q, Query)
        # did.query.Query stores search_structure as a list of dicts
        self.assertEqual(q.search_structure[0]['field'], 'test.field')

if __name__ == '__main__':
    unittest.main()
