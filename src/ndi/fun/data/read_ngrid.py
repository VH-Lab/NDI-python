import numpy as np
import os
import warnings

# MATLAB's writengrid writes little-endian ('ieee-le'); read the same way on
# every platform rather than in the machine's native byte order.
_DTYPE_MAP = {
    'double': '<f8',
    'single': '<f4',
    'int8': 'i1',
    'uint8': 'u1',
    'int16': '<i2',
    'uint16': '<u2',
    'int32': '<i4',
    'uint32': '<u4',
    'int64': '<i8',
    'uint64': '<u8',
    'char': 'u1',      # MATLAB fread 'char' reads 8-bit characters
    'logical': '?',
}


def read_ngrid(filename_or_fileobj, data_size, data_type='double'):
    """
    Read an n-dimensional matrix from a binary file.

    Args:
        filename_or_fileobj (str, os.PathLike, or file object): Path to the
            file, or an object to read from. Accepted objects are:
              * DID-python file objects (did.file.Fileobj, ReadOnlyFileobj,
                and the binary document objects returned by
                database_openbinarydoc), which expose ``fread``; an object
                that is not open (``fid is None``) is opened read-only here
                and closed again after reading, and one that is already open
                is read from its current position and left open for its owner
                to close;
              * any binary file-like object with ``read`` (an open file,
                io.BytesIO, ...), which is read and left open.
        data_size (list of int): Dimensions of the matrix.
        data_type (str): 'double', 'single', 'int8', 'uint8', etc.

    Returns:
        np.ndarray: N-dimensional matrix of shape ``data_size``.

    The file holds the elements in MATLAB (column-major, little-endian)
    order, as written by MATLAB's writengrid or ndi.fun.data.write_ngrid.
    """
    if data_type not in _DTYPE_MAP:
        # As before (and as MATLAB's readngrid warns), fall back to double.
        warnings.warn(f"Unknown data_type '{data_type}'; reading as 'double'.")
        data_type = 'double'
    np_dtype = np.dtype(_DTYPE_MAP[data_type])
    data_size = [int(d) for d in np.atleast_1d(data_size)]
    count = int(np.prod(data_size))
    nbytes = count * np_dtype.itemsize

    if isinstance(filename_or_fileobj, (str, os.PathLike)):
        if not os.path.isfile(filename_or_fileobj):
            raise FileNotFoundError(f"File not found: {filename_or_fileobj}")
        with open(filename_or_fileobj, 'rb') as f:
            raw = f.read(nbytes)
    else:
        raw = _read_from_object(filename_or_fileobj, nbytes)

    if raw is None:
        raw = b''
    if len(raw) != nbytes:
        raise ValueError(
            f"Read {len(raw) // np_dtype.itemsize} elements; expected {count} "
            f"for data_size {data_size}. Check data_size and data_type.")

    x = np.frombuffer(raw, dtype=np_dtype, count=count)
    # Elements are stored in column-major (MATLAB) order.
    return x.reshape(data_size, order='F').astype(np_dtype.newbyteorder('='))


def _read_from_object(obj, nbytes):
    """Read NBYTES raw bytes from a DID file object or a file-like object."""
    if hasattr(obj, 'fread'):
        # DID-python file object. Open it here only if it is not open, and in
        # that case close it again; an open object belongs to the caller.
        opened_here = False
        if getattr(obj, 'fid', None) is None and hasattr(obj, 'fopen'):
            obj.fopen()
            if getattr(obj, 'fid', None) is None:
                name = getattr(obj, 'fullpathfilename', '')
                raise FileNotFoundError(f"Could not open file: {name}")
            opened_here = True
        try:
            return obj.fread(nbytes)
        finally:
            if opened_here:
                obj.fclose()
    if hasattr(obj, 'read'):
        return obj.read(nbytes)
    raise TypeError(
        "filename_or_fileobj must be a path, a DID file object, or a binary "
        "file-like object with a read() method.")
