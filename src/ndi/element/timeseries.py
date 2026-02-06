from . import Element
from ..time.timeseries import TimeSeries

class Timeseries(Element, TimeSeries):
    """
    An NDI element with time series data.
    """

    def __init__(self, session, name, reference, element_subtype, underlying_element, direct, author):
        """
        Initializes a new Timeseries element.
        """
        super().__init__(session, name, reference, element_subtype, underlying_element, direct, author)

    def readtimeseries(self, timeref_or_epoch, t0, t1):
        """
        Reads time series data from the element.

        If the element is direct, it reads from the underlying element. Otherwise,
        it reads from the element's own data.
        """
        if self.direct:
            return self.underlying_element.readtimeseries(timeref_or_epoch, t0, t1)
        else:
            # This is a simplified implementation. The full implementation will
            # require the syncgraph and database components.
            raise NotImplementedError("Reading from non-direct elements is not yet implemented.")

    def addepoch(self, epoch_id, epoch_clock, t0_t1, timepoints, datapoints, epoch_ids=None):
        """
        Adds an epoch to the element.

        This is a simplified implementation. The full implementation will
        require the database and file handling components.
        """
        if self.direct:
            raise ValueError("Cannot add external observations to an element that is directly based on another element.")

        # This is a simplified implementation.
        raise NotImplementedError("Adding epochs is not yet implemented.")

    def samplerate(self, epoch):
        """
        Calculates the sample rate for a given epoch.

        This is a simplified implementation.
        """
        raise NotImplementedError("Sample rate calculation is not yet implemented.")
