import unittest
from unittest.mock import Mock
from ndi.element.timeseries import Timeseries

class TestElement(unittest.TestCase):

    def test_create_timeseries_element(self):
        """
        Tests the creation of a Timeseries element.
        """
        mock_session = Mock()
        mock_underlying_element = Mock()

        element = Timeseries(
            session=mock_session,
            name='my_element',
            reference='ref1',
            element_subtype='subtype',
            underlying_element=mock_underlying_element,
            direct=True,
            author='test@example.com'
        )

        self.assertIsInstance(element, Timeseries)
        self.assertEqual(element.name, 'my_element')
        self.assertEqual(element.reference, 'ref1')
        self.assertEqual(element.element_subtype, 'subtype')
        self.assertIs(element.underlying_element, mock_underlying_element)
        self.assertTrue(element.direct)
        self.assertEqual(element.author, 'test@example.com')

if __name__ == '__main__':
    unittest.main()
