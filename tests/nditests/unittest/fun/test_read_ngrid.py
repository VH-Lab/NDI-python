import io
import os
import pathlib
import shutil
import tempfile
import unittest

import numpy as np

from ndi.fun.data import read_ngrid, write_ngrid

try:
    from did.file import Fileobj, ReadOnlyFileobj
    HAVE_DID = True
except ImportError:  # pragma: no cover - did is a declared dependency
    HAVE_DID = False


class TestReadNgrid(unittest.TestCase):
    """read_ngrid reads what write_ngrid (or MATLAB's writengrid) wrote, from
    a path or from a file object, including DID file objects such as those
    database_openbinarydoc returns."""

    def setUp(self):
        self.root = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.root)

    def _write(self, x, name, data_type='double'):
        fname = os.path.join(self.root, name)
        write_ngrid(x, fname, data_type)
        return fname

    def test_path_round_trip_2d(self):
        x = np.random.rand(4, 3)
        fname = self._write(x, 'a.ngrid')
        np.testing.assert_array_equal(read_ngrid(fname, [4, 3]), x)

    def test_path_round_trip_3d_and_pathlike(self):
        x = np.random.rand(3, 4, 2)
        fname = self._write(x, 'b.ngrid')
        y = read_ngrid(pathlib.Path(fname), list(x.shape))
        self.assertEqual(y.shape, x.shape)
        np.testing.assert_array_equal(y, x)

    def test_column_major_little_endian_layout(self):
        # MATLAB writes column-major, little-endian; build such a file by hand.
        x = np.arange(6, dtype=float).reshape(2, 3)
        fname = os.path.join(self.root, 'c.ngrid')
        with open(fname, 'wb') as f:
            f.write(x.flatten(order='F').astype('<f8').tobytes())
        np.testing.assert_array_equal(read_ngrid(fname, [2, 3]), x)

    def test_integer_type(self):
        x = np.arange(12, dtype=np.int16).reshape(3, 4)
        fname = self._write(x, 'd.ngrid', 'int16')
        y = read_ngrid(fname, [3, 4], 'int16')
        self.assertEqual(y.dtype, np.int16)
        np.testing.assert_array_equal(y, x)

    def test_file_like_object_is_read_and_left_open(self):
        x = np.random.rand(2, 5)
        buf = io.BytesIO(x.flatten(order='F').astype('<f8').tobytes())
        np.testing.assert_array_equal(read_ngrid(buf, [2, 5]), x)
        self.assertFalse(buf.closed)

    @unittest.skipUnless(HAVE_DID, 'did is not installed')
    def test_unopened_did_fileobj_is_opened_and_closed(self):
        x = np.random.rand(5, 2)
        fname = self._write(x, 'e.ngrid')
        fo = ReadOnlyFileobj(fullpathfilename=fname)
        self.assertIsNone(fo.fid)
        np.testing.assert_array_equal(read_ngrid(fo, [5, 2]), x)
        self.assertIsNone(fo.fid, 'an object read_ngrid opened should be closed again')

    @unittest.skipUnless(HAVE_DID, 'did is not installed')
    def test_open_did_fileobj_is_read_and_left_open(self):
        # The case database_openbinarydoc produces: an already-open object.
        x = np.random.rand(2, 3, 2)
        fname = self._write(x, 'f.ngrid')
        fo = ReadOnlyFileobj(fullpathfilename=fname)
        fo.fopen()
        try:
            self.assertIsNotNone(fo.fid)
            np.testing.assert_array_equal(read_ngrid(fo, [2, 3, 2]), x)
            self.assertIsNotNone(fo.fid, 'an object open on entry should be left open')
        finally:
            fo.fclose()

    def test_wrong_size_raises(self):
        fname = self._write(np.random.rand(2, 2), 'g.ngrid')
        with self.assertRaises(ValueError):
            read_ngrid(fname, [3, 3])

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            read_ngrid(os.path.join(self.root, 'missing.ngrid'), [2, 2])

    def test_unknown_type_warns_and_reads_double(self):
        x = np.random.rand(2, 2)
        fname = self._write(x, 'h.ngrid')
        with self.assertWarns(UserWarning):
            y = read_ngrid(fname, [2, 2], 'notatype')
        np.testing.assert_array_equal(y, x)


if __name__ == '__main__':
    unittest.main()
