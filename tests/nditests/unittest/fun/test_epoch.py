import unittest
from unittest.mock import MagicMock
from ndi.fun.epoch import epoch_id_to_element, filename_to_epoch_id

class TestEpoch(unittest.TestCase):
    def test_epoch_id_to_element(self):
        session = MagicMock()
        elem1 = MagicMock()
        # Mock objects create attributes on access, so we must be careful.
        # We can use spec or configure explicitly.
        elem1.epoch_table = None # Ensure this is None if we want to test fallback, or just set it.
        elem1.epochtable = [{'epoch_id': 'ep1'}, {'epoch_id': 'ep2'}]
        elem1.name = 'element1'

        elem2 = MagicMock()
        elem2.epoch_table = None
        elem2.epochtable = [{'epoch_id': 'ep3'}]
        elem2.name = 'element2'

        session.get_elements.return_value = [elem1, elem2]
        session.getelements.return_value = [elem1, elem2]

        # Test finding one epoch
        res = epoch_id_to_element(session, 'ep2')
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0], elem1)

        # Test finding multiple
        res = epoch_id_to_element(session, ['ep3', 'ep1'])
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0], elem2)
        self.assertEqual(res[1], elem1)

        # Test not found
        res = epoch_id_to_element(session, 'ep99')
        self.assertEqual(len(res), 1)
        self.assertIsNone(res[0])

    def test_filename_to_epoch_id(self):
        session = MagicMock()
        dev = MagicMock()
        # Explicitly set epoch_table to use it, avoiding mock magic issues
        dev.epoch_table = [
            {
                'epoch_id': 'ep1',
                'underlying_epochs': {'underlying': ['fileA.dat', 'fileB.dat']}
            },
            {
                'epoch_id': 'ep2',
                'underlying_epochs': {'underlying': ['fileC.dat']}
            }
        ]

        session.daq_system_load.return_value = [dev]
        session.daqsystem_load.return_value = [dev]

        # Find by filename
        res = filename_to_epoch_id(session, 'fileB.dat')
        self.assertEqual(res[0], 'ep1')

        res = filename_to_epoch_id(session, 'fileC.dat')
        self.assertEqual(res[0], 'ep2')

        res = filename_to_epoch_id(session, 'fileZ.dat')
        self.assertIsNone(res[0])

if __name__ == '__main__':
    unittest.main()
