import numpy as np

class TimeMapping:
    def __init__(self, mapping=None):
        if mapping is None:
            self.mapping = [1, 0]
        else:
            self.mapping = mapping

        try:
            self.map(0)
        except Exception as e:
            raise ValueError(f"A test of the mapping with t_in = 0 failed: {e}")

    def map(self, t_in):
        return np.polyval(self.mapping, t_in)
