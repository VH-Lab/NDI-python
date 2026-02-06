import unittest
from unittest.mock import Mock
from ndi.time.syncgraph import SyncGraph
from ndi.time.syncrule import SyncRule

class MockSyncRule(SyncRule):
    def apply(self, epochnode_a, epochnode_b):
        return 1.0, None
    def search_query(self):
        pass

class TestTime(unittest.TestCase):

    def test_syncgraph_creation(self):
        mock_session = Mock()
        sg = SyncGraph(mock_session)
        self.assertIsInstance(sg, SyncGraph)
        self.assertEqual(sg.session, mock_session)

    def test_syncgraph_add_rule(self):
        mock_session = Mock()
        sg = SyncGraph(mock_session)
        rule = MockSyncRule()
        sg.addrule(rule)
        self.assertIn(rule, sg.rules)

    def test_syncrule_creation(self):
        rule = MockSyncRule()
        self.assertIsInstance(rule, SyncRule)

if __name__ == '__main__':
    unittest.main()
