import unittest
from unittest.mock import Mock, MagicMock
from ndi.app.markgarbage import MarkGarbage

class TestMarkGarbage(unittest.TestCase):
    def test_instantiation(self):
        session = Mock()
        app = MarkGarbage(session)
        self.assertIsNotNone(app)

    def test_mark_valid_interval(self):
        session = MagicMock()
        epochset_obj = Mock()
        timeref = Mock()

        app = MarkGarbage(session)
        app.load_valid_interval = MagicMock(return_value=([], None)) # mock the load
        app.clear_valid_interval = MagicMock() # mock the clear

        app.mark_valid_interval(epochset_obj, 0, timeref, 1, timeref)

        # check that the session was called to save the document
        session.database_add.assert_called_once()
