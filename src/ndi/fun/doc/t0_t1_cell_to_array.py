import numpy as np

def t0_t1_cell_to_array(t0t1_in):
    """
    Convert a t0..t1 interval expressed as a cell in an epochtable entry as array.

    Args:
        t0t1_in (list of list/tuple): Input t0t1 intervals. Each element is [t0, t1].

    Returns:
        np.ndarray: 2xN array suitable for inclusion in an ndi.document object.
    """
    if not t0t1_in:
        return np.zeros((2, 0))

    N = len(t0t1_in)
    t0t1_out = np.zeros((2, N))

    for k, item in enumerate(t0t1_in):
        if len(item) >= 2:
            t0t1_out[0, k] = item[0]
            t0t1_out[1, k] = item[1]
        else:
            # Handle malformed input?
            pass

    return t0t1_out
