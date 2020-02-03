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
    def add_experiment(self, experiment):
        pass

    @abstractmethod
    def create_collection(self, name, **fields):
        pass

    @abstractmethod
    def add(self, ndi_object):
        pass

    @abstractmethod
    def update(self, ndi_object):
        pass

    @abstractmethod
    def upsert(self, ndi_object):
        pass

    @abstractmethod
    def delete(self, ndi_object):
        pass

    @abstractmethod
    def find_by_id(self, ndi_class, id_):
        pass

    @abstractmethod
    def update_by_id(self, ndi_class, id_, payload):
        pass

    @abstractmethod
    def delete_by_id(self, ndi_class, id_):
        pass

    @abstractmethod
    def find(self, ndi_class, query):
        pass

    @abstractmethod
    def update_many(self, ndi_class, query, payload):
        pass

    @abstractmethod
    def delete_many(self, ndi_class, query):
        pass
