import abc

class TimeSeries(abc.ABC):
    """
    A mix-in class for objects that have time series data.
    """

    @abc.abstractmethod
    def readtimeseries(self, timeref_or_epoch, t0, t1):
        """
        Read time series data from an object.

        This is an abstract method and must be implemented in the subclass.

        Args:
            timeref_or_epoch: An ndi.time.timereference object or an epoch id.
            t0: The starting time.
            t1: The ending time.

        Returns:
            A tuple of (data, t, timeref).
        """
        raise NotImplementedError("This function must be implemented in the subclass.")
