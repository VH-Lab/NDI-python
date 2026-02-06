from ..probe import Probe
from ...time.timeseries import TimeSeries
import abc

class Timeseries(Probe, TimeSeries):
    """
    An abstract class for time series probes.
    """

    def __init__(self, session, name, reference, type_, subject_id):
        """
        Initializes a new Timeseries probe.
        """
        super().__init__(session, name, reference, type_, subject_id)

    @abc.abstractmethod
    def readtimeseries(self, timeref_or_epoch, t0, t1):
        """
        Reads time series data from the probe.
        """
        # This is a complex method that will require more components to be ported.
        raise NotImplementedError("This method is not yet implemented.")
