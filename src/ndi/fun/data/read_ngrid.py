import numpy as np
import os

def read_ngrid(filename_or_fileobj, data_size, data_type='double'):
    """
    Read an n-dimensional matrix from a binary file.

    Args:
        filename_or_fileobj (str or fileobj): Path to file or file object.
        data_size (list of int): Dimensions of matrix.
        data_type (str): 'double', 'single', 'int8', 'uint8', etc.

    Returns:
        np.ndarray: N-dimensional matrix.
    """
    dtype_map = {
        'double': np.float64,
        'single': np.float32,
        'int8': np.int8,
        'uint8': np.uint8,
        'int16': np.int16,
        'uint16': np.uint16,
        'int32': np.int32,
        'uint32': np.uint32,
        'int64': np.int64,
        'uint64': np.uint64,
        'char': np.char, # ?
        'logical': np.bool_
    }

    np_dtype = dtype_map.get(data_type, np.float64)

    if isinstance(filename_or_fileobj, str):
        if not os.path.isfile(filename_or_fileobj):
            raise FileNotFoundError(f"File not found: {filename_or_fileobj}")

        with open(filename_or_fileobj, 'rb') as f:
            # Numpy reads in C-order by default, but Matlab writes in F-order (column-major)
            # data_size is (rows, cols, depth...)
            # We should read as flat then reshape in 'F' order
            count = np.prod(data_size)
            x = np.fromfile(f, dtype=np_dtype, count=count)
            x = x.reshape(data_size, order='F')

    else: # file object
        # Assuming read method
        count = np.prod(data_size)
        x = np.fromfile(filename_or_fileobj, dtype=np_dtype, count=count)
        x = x.reshape(data_size, order='F')

    return x
