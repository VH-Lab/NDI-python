from ..channel import Channel
from ..probe import Probe
from ..epoch import Epoch

class MockReader:
    def __init__(self, epoch_files=[]):
        self.epoch_files = epoch_files
        self.__build_epoch_probe_map()

    def __build_epoch_probe_map(self):
        self.probes = [
            Probe('intan', 1, 'sharp_vm'),
            Probe('intan', 2, 'sharp_vm')
        ]
        self.epochs = [
            Epoch(),
            Epoch(),
            Epoch()
        ]
        self.channels = [
            Channel('ai1', 1, 'analog_in', 't1/test.data', self.epochs[0].id, self.probes[0].id),
            Channel('di2', 2, 'digital_in', 't2/test.data', self.epochs[1].id, self.probes[0].id),
            Channel('aux3', 3, 'auxiliary', 't3/test.data', self.epochs[2].id, self.probes[1].id)
        ]

    def get_probes(self):
        return self.probes

    def get_epochs(self):
        return self.epochs

    def get_channels(self):
        return self.channels
