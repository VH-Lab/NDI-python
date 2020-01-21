from abc import ABC, abstractmethod

from ..experiment import Experiment
from ..daq_system import DaqSystem
from ..probe import Probe
from ..epoch import Epoch
from ..channel import Channel


class BaseDB(ABC):
    _collections = {
        Experiment: None,
        DaqSystem: None,
        Probe: None,
        Epoch: None,
        Channel: None
    }

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add_experiment(self):
        pass

    @abstractmethod
    def create_collections(self):
        pass

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def find(self):
        pass
