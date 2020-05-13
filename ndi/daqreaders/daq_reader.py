from abc import ABC, abstractmethod


class DaqReader(ABC):
    def __init__(self, filename):
        self.filename = filename
    
    @abstractmethod
    def samplerate(self, channel_number):
        pass
