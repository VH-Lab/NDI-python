import unittest
from ndi.probe.timeseries.mfdaq import Mfdaq
from unittest.mock import Mock

class TestMfdaq(unittest.TestCase):
    def test_instantiation(self):
        # mock the session object
        session = Mock()
        probe = Mfdaq(session, 'test_probe', '1', 'test_type', 'subject_1')
        self.assertIsNotNone(probe)

if __name__ == '__main__':
    unittest.main()
