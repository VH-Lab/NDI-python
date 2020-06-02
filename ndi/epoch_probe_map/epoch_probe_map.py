from abc import ABC, abstractmethod

class EpochProbeMap(ABC):
    @abstractmethod
    def __init__(self, daq_reader, epoch_sets, ctx):
        pass

    @abstractmethod
    def get_epochs_probes_channels(self):
        epochs = []
        probes = []
        channels = []
        return epochs, probes, channels
