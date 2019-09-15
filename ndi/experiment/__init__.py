import uuid

from ndi.schema.Experiment import Experiment as AbstractExperiment


class Experiment(AbstractExperiment):
    """The class that implements the basic structure of an experiment, including a DAQ system list, sync graph, cache, reference, and a unique reference string."""

    def __init__(self, name, path, unique_reference=None):
        self.name = name
        self.path = path
        self.unique_reference = unique_reference
        self.daq_systems = []

    def daq_system_add(self, daq_system):
        """Add a new ndi.daqsystem.DaqSystem to this experiment"""
        self.daq_systems.append(daq_system)

    def get_probes(self, name=None, reference=None, type=None):
        """Find probes associated with added DAQ systems."""
        pass
