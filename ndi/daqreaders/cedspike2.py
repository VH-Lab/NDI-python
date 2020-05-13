from .daq_reader import DaqReader
from neo.io import Spike2IO

class CEDSpike2(DaqReader):
    def __init__(self, filename):
        self.filename = filename
        self.__reader = Spike2IO(filename)

    def samplerate(self, channel_number):
        channel_index = self.__reader.channel_id_to_index([channel_number - 1]) 
        return self.__reader.get_signal_sampling_rate(channel_index)
