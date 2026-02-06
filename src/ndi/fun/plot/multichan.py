import matplotlib.pyplot as plt

def multichan(data, t, space):
    """
    Plots multiple channels.

    Args:
        data (np.ndarray): NUMSAMPLES x NUMCHANNELS matrix.
        t (np.ndarray): Time vector.
        space (float): Spacing between channels.

    Returns:
        list: List of plot handles.
    """
    handles = []

    # Check dimensions
    # Assuming data is (samples, channels)
    if data.ndim != 2:
        raise ValueError("Data must be 2D array")

    num_channels = data.shape[1]

    for i in range(num_channels):
        h = plt.plot(t, i * space + data[:, i], color=[0.7, 0.7, 0.7])
        handles.append(h)

    return handles
