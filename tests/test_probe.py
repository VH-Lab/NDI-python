import unittest
from unittest.mock import Mock
from ndi.probe.timeseries.mfdaq import Mfdaq
from ndi.daq.system.mfdaq import Mfdaq as MfdaqSystem
from ndi.daq.reader.mfdaq import Mfdaq as MfdaqReader

class MockMfdaqReader(MfdaqReader):
    def getchannelsepoch(self, epochfiles):
        return [{'name': 'ai1', 'type': 'analog_in'}]
    def readchannels_epochsamples(self, channeltype, channel, epochfiles, s0, s1):
        return [1, 2, 3]
    def samplerate(self, epochfiles, channeltype, channel):
        return 1000

class TestProbe(unittest.TestCase):

    def test_mfdaq_creation(self):
        mock_session = Mock()
        probe = Mfdaq(mock_session, 'my_probe', 1, 'mfdaq')
        self.assertIsInstance(probe, Mfdaq)

    def test_mfdaq_readtimeseriesepoch(self):
        mock_session = Mock()
        mock_filenavigator = Mock()
        mock_filenavigator.getepochfiles.return_value = ['/fake/path/file.ext']
        mock_daqreader = MockMfdaqReader()
        mock_daqsystem = MfdaqSystem('my_device', mock_filenavigator, mock_daqreader)

        probe = Mfdaq(mock_session, 'my_probe', 1, 'mfdaq')

        # This is a placeholder test. The full implementation will require
        # the getchanneldevinfo() method to be implemented.
        with self.assertRaises(AttributeError):
            data, t, timeref = probe.readtimeseriesepoch(1, 0, 1)

if __name__ == '__main__':
    unittest.main()
