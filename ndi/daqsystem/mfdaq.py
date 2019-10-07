from . import DaqSystem
from .daqreader import DaqReader


class DaqSystemMultiFunction(DaqSystem):
    """This object allows one to address multifunction data acquisition systems that sample a variety of data types potentially simultaneously. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read_channels(self, channel_type, channels, timeref_or_epoch=None):
        if timeref_or_epoch:
            # Epoch mapping
            raise Exception('Epoch mapping is not yet implemented')
        else:
            return self.read_channels_samples(channel_type, channels, timeref_or_epoch)

    def read_channels_samples(self, channel_type, channels, epoch):
        return self.daq_reader.read_channels_epoch_samples(channel_type, channels, epoch)


class DaqReaderMultiFunction(DaqReader):
    """This object allows one to address multifunction data acquisition systems that sample a variety of data types potentially simultaneously. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read_channels_epoch_samples(self, channel_type, channel, epoch):
        """Read data based on specified channels."""
        return []
