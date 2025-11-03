import abc

class Mfdaq(abc.ABC):
    """
    An abstract class for reading data from a multifunction DAQ.
    """

    @abc.abstractmethod
    def getchannelsepoch(self, epochfiles):
        raise NotImplementedError

    @abc.abstractmethod
    def readchannels_epochsamples(self, channeltype, channel, epochfiles, s0, s1):
        raise NotImplementedError

    @abc.abstractmethod
    def samplerate(self, epochfiles, channeltype, channel):
        raise NotImplementedError
