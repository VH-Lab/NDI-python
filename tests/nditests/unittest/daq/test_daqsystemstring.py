import unittest
from ndi.daq.daqsystemstring import DaqSystemString

class TestDaqSystemString(unittest.TestCase):

    def test_daqsystemstring_creation_from_string(self):
        dss = DaqSystemString('mydevice:ai1-5,7,23')
        self.assertEqual(dss.devicename, 'mydevice')
        self.assertEqual(dss.channeltype, ['ai', 'ai', 'ai', 'ai', 'ai', 'ai', 'ai'])
        self.assertEqual(dss.channellist, [1, 2, 3, 4, 5, 7, 23])

    def test_daqsystemstring_creation_from_parts(self):
        dss = DaqSystemString('mydevice', ['ai', 'ai', 'ai'], [1, 2, 3])
        self.assertEqual(dss.devicename, 'mydevice')
        self.assertEqual(dss.channeltype, ['ai', 'ai', 'ai'])
        self.assertEqual(dss.channellist, [1, 2, 3])

    def test_daqsystemstring_to_string(self):
        dss = DaqSystemString('mydevice', ['ai', 'ai', 'ai'], [1, 2, 3])
        self.assertEqual(str(dss), 'mydevice:ai1-3')

if __name__ == '__main__':
    unittest.main()
