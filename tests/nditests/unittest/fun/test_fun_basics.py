import unittest
import os
import shutil
import tempfile
import numpy as np
import datetime
from ndi.fun import pseudorandomint, stimulus_temporal_frequency, channel_name_to_prefix_number, name_to_variable_name, timestamp, find_calc_directories
from ndi.fun.file import md5, date_created, date_updated
from ndi.fun.data import read_ngrid, write_ngrid
from ndi.fun.doc import all_types
from ndi.common.path_constants import PathConstants

class TestNdiFun(unittest.TestCase):
    def test_pseudorandomint(self):
        val = pseudorandomint()
        self.assertIsInstance(val, int)

    def test_channel_name_to_prefix_number(self):
        prefix, number = channel_name_to_prefix_number("Channel 1")
        self.assertEqual(prefix, "Channel")
        self.assertEqual(number, 1)

    def test_name_to_variable_name(self):
        self.assertEqual(name_to_variable_name("My Variable"), "myVariable")

    def test_timestamp(self):
        ts = timestamp()
        self.assertIsInstance(ts, str)

    def test_md5(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(b"hello world")
            fname = f.name
        try:
            checksum = md5(fname)
            self.assertEqual(checksum, "5eb63bbbe01eeed093cb22bb8f5acdc3")

            dc = date_created(fname)
            self.assertIsInstance(dc, datetime.datetime)

            du = date_updated(fname)
            self.assertIsInstance(du, datetime.datetime)
        finally:
            os.remove(fname)

    def test_ngrid(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            fname = f.name
        try:
            data = np.random.rand(5, 5)
            write_ngrid(data, fname)
            read_data = read_ngrid(fname, [5, 5])
            np.testing.assert_array_almost_equal(data, read_data)
        finally:
            os.remove(fname)

    def test_all_types(self):
        # Just check it runs
        types = all_types()
        self.assertIsInstance(types, list)

    def test_find_calc_directories(self):
        dirs = find_calc_directories()
        self.assertIsInstance(dirs, list)

if __name__ == '__main__':
    unittest.main()
