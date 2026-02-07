import unittest
from unittest.mock import Mock
from ndi.daq.system.mfdaq import Mfdaq
from ndi.daq.reader.mfdaq import Mfdaq as MfdaqReader

class MockMfdaqReader(MfdaqReader):
    def getchannelsepoch(self, epochfiles):
        return [{'name': 'ai1', 'type': 'analog_in'}]
    def readchannels_epochsamples(self, channeltype, channel, epochfiles, s0, s1):
        return [1, 2, 3]
    def samplerate(self, epochfiles, channeltype, channel):
        return 1000

class TestDaqSystem(unittest.TestCase):

    def test_mfdaq_creation(self):
        mock_filenavigator = Mock()
        mock_daqreader = MockMfdaqReader()

        mfdaq = Mfdaq('my_device', mock_filenavigator, mock_daqreader)
        self.assertIsInstance(mfdaq, Mfdaq)

    def test_mfdaq_getchannels(self):
        mock_filenavigator = Mock()
        mock_filenavigator.numepochs.return_value = 1
        mock_filenavigator.getepochfiles.return_value = ['/fake/path/file.ext']
        mock_daqreader = MockMfdaqReader()

        mfdaq = Mfdaq('my_device', mock_filenavigator, mock_daqreader)
        channels = mfdaq.getchannels()
        self.assertEqual(len(channels), 1)
        self.assertEqual(channels[0]['name'], 'ai1')

if __name__ == '__main__':
    unittest.main()
