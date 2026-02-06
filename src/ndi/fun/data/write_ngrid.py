import numpy as np

def write_ngrid(x, file_path, data_type='double'):
    """
    Write an n-dimensional matrix to a binary file.

    Args:
        x (np.ndarray): Data to write.
        file_path (str): Path to output file.
        data_type (str): Data type to write as.
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
        'logical': np.bool_
    }

    np_dtype = dtype_map.get(data_type, np.float64)

    # Ensure x is numpy array
    if not isinstance(x, np.ndarray):
        x = np.array(x)

    # Cast to type
    x_casted = x.astype(np_dtype)

    with open(file_path, 'wb') as f:
        # Write in Fortran order (column-major) to match Matlab
        # To do this correctly:
        # 1. Flatten in F order
        # 2. Write to file
        x_casted.flatten(order='F').tofile(f)
