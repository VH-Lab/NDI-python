from . import System
from ..reader.mfdaq import Mfdaq as MfdaqReader

class Mfdaq(System):
    """
    A multifunction DAQ object.
    """

    def __init__(self, name, filenavigator, daqreader):
        """
        Initializes a new Mfdaq object.
        """
        super().__init__(name, filenavigator, daqreader)
        if not isinstance(self.daqreader, MfdaqReader):
            raise TypeError("The daqreader must be of type ndi.daq.reader.mfdaq.")

    def getchannels(self):
        """
        Lists the channels available on this device.
        """
        channels = []
        for i in range(self.filenavigator.numepochs()):
            epoch_files = self.filenavigator.getepochfiles(i + 1)
            channels.extend(self.daqreader.getchannelsepoch(epoch_files))
        # Poor-man's unique
        return list({v['name']:v for v in channels}.values())

    def readchannels_epochsamples(self, channeltype, channel, epoch, s0, s1):
        """
        Reads data from the specified channels.
        """
        epoch_files = self.filenavigator.getepochfiles(epoch)
        return self.daqreader.readchannels_epochsamples(channeltype, channel, epoch_files, s0, s1)

    def samplerate(self, epoch, channeltype, channel):
        """
        Returns the sample rate for the specified channels.
        """
        epoch_files = self.filenavigator.getepochfiles(epoch)
        return self.daqreader.samplerate(epoch_files, channeltype, channel)
