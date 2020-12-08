from __future__ import annotations
import ndi.types as T
from .did_adapter import DIDAdapter

class Context:
    def __init__(
        self, 
        data_interface_database = None,
        daq_systems: T.List[T.DaqSystem] = [],
        daq_readers_map: T.Dict[str, T.DaqReader] = {}
    ):
        self._did_adapter = DIDAdapter(self, data_interface_database)
        self.daq_systems = daq_systems
        self.daq_readers_map = daq_readers_map

    @property
    def bin(self):
        # TODO: phase need for this out by moving binary feature implementations from ndi to did 
        return self._did_adapter.did.bin
    
    @property
    def did(self):
        return self._did_adapter
        
    @property
    def data_interface_database(self):
        return self._did_adapter
    @data_interface_database.setter
    def data_interface_database(self, did_instance):
        self._did_adapter = DIDAdapter(self, did_instance)

    def load_daq_system(self, daq_system):
        if daq_system.id not in [ds.id for ds in self.daq_systems]:
            self.daq_systems.append(daq_system)
        self._load_daq_reader(daq_system.daq_reader)

    def _load_daq_reader(self, daq_reader):
        """Loads a DaqReader to the context. Should be handled by load_daq_system."""
        reader_name = daq_reader.__name__
        if reader_name not in self.daq_readers_map:
            self.daq_readers_map[reader_name] = daq_reader
