from .base_db import BaseDB
from pathlib import Path

NDI_DB_DIR = '.ndi'

class FileSystem(BaseDB):
    def __init__(self, exp_dir):
        self.exp_dir = Path(exp_dir)
        self.db_dir = self.exp_dir / NDI_DB_DIR

        # Initializing FS Database
        if self.exp_dir.exists() and self.exp_dir.is_dir():
            self.create_collections()
        else:
            raise FileNotFoundError(f'No such file or directory: \'{self.exp_dir}\'')

    def add_experiment(self, experiment):
        self._collections[type(experiment)].add(experiment)
        for daqsystem in experiment.daqsystems:
            self._collections[type(daqsystem)].add(daqsystem)
            daqreader = daqsystem.daq_reader()

            for probe in daqreader.get_probes():
                self._collections[type(probe)].add(probe)

            for epoch in daqreader.get_epochs():
                self._collections[type(epoch)].add(epoch)
        
            for channel in daqreader.get_channels():
                channel.id = channel.probe_id + channel.epoch_id
                self._collections[type(channel)].add(channel)

    def create_collections(self):
        for collection in self._collections:
            self._collections[collection] = Collection(self.db_dir / f'{collection.__name__.lower()}s')

    def add(self, ndi_object):
        self._collections[type(ndi_object)].add(ndi_object)

    def find_by_id(self, ndi_class, id_):
        return self._collections[ndi_class].find_by_id(ndi_class, id_)

    def find(self, ndi_class, **kwargs):
        return [
            ndi_object
            for ndi_object in self._collections[ndi_class].find(ndi_class)
            for key, value in kwargs.items()
            if getattr(ndi_object, key) == value
        ]

class Collection:
    def __init__(self, collection_dir):
        self.collection_dir = Path(collection_dir)

        # Initializing Collection
        self.collection_dir.mkdir(parents=True, exist_ok=True)

    def add(self, ndi_object):
        (self.collection_dir / f'{ndi_object.id}.dat').write_bytes(ndi_object.serialize())

    def find_by_id(self, ndi_class, id_):
        return ndi_class.frombuffer((self.collection_dir / f'{id_}.dat').read_bytes())

    def find(self, ndi_class):
        return [
            ndi_class.frombuffer(file.read_bytes())
            for file in self.collection_dir.glob('*.dat')
        ]
