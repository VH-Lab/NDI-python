import unittest
from ndi.fun import timestamp
from ndi.fun import name_to_variable_name
from ndi.fun import channel_name_to_prefix_number

class TestFun(unittest.TestCase):

    def test_timestamp(self):
        """
        Tests the timestamp function.
        """
        ts = timestamp.timestamp()
        self.assertIsInstance(ts, str)
        self.assertRegex(ts, r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{6}')

    def test_name_to_variable_name(self):
        """
        Tests the name_to_variable_name function.
        """
        self.assertEqual(name_to_variable_name.name_to_variable_name("hello world"), "helloWorld")
        self.assertEqual(name_to_variable_name.name_to_variable_name("hello-world"), "helloWorld")
        self.assertEqual(name_to_variable_name.name_to_variable_name("hello:world"), "helloWorld")
        self.assertEqual(name_to_variable_name.name_to_variable_name("1hello world"), "var_1helloWorld")
        self.assertEqual(name_to_variable_name.name_to_variable_name(""), "")
        self.assertEqual(name_to_variable_name.name_to_variable_name("  "), "")

    def test_channel_name_to_prefix_number(self):
        """
        Tests the channel_name_to_prefix_number function.
        """
        prefix, number = channel_name_to_prefix_number.channel_name_to_prefix_number("ai5")
        self.assertEqual(prefix, "ai")
        self.assertEqual(number, 5)

        prefix, number = channel_name_to_prefix_number.channel_name_to_prefix_number("  din10  ")
        self.assertEqual(prefix, "din")
        self.assertEqual(number, 10)

        with self.assertRaises(ValueError):
            channel_name_to_prefix_number.channel_name_to_prefix_number("no_number")

        with self.assertRaises(ValueError):
            channel_name_to_prefix_number.channel_name_to_prefix_number("1starts_with_number")


if __name__ == '__main__':
    unittest.main()
