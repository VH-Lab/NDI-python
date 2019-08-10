import uuid

from ndi.schema import Experiment as AbstractExperiment
from ndi.schema import SyncGraph


class Experiment(AbstractExperiment):
    """The class that implements the basic structure of an experiment, including a DAQ system list, sync graph, cache, reference, and a unique reference string."""

    def __init__(self, name, path, unique_reference=None):
        self.name = name
        self.path = path
        self.unique_reference = unique_reference
        self.daq_systems = []

    def daqSystemAdd(self, daqSystem):
        """Add a new ndi.daqsystem.DaqSystem to this experiment"""
        self.daq_systems.push(daqSystem)
