import unittest
from ndi.probe.timeseries import Timeseries

class TestTimeseries(unittest.TestCase):

    def test_instantiation(self):
        # We can't instantiate an abstract class directly,
        # so we'll create a dummy concrete class for testing.
        class ConcreteTimeseries(Timeseries):
            def readtimeseries(self, timeref_or_epoch, t0, t1):
                return "dummy data"
            def buildepochtable(self):
                return []

        # If this line runs without a TypeError, the metaclass conflict is resolved.
        probe = ConcreteTimeseries(None, 'test_probe', '1', 'test_type', 'subject_1')
        self.assertIsNotNone(probe)

if __name__ == '__main__':
    unittest.main()
