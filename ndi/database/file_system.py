from .base_db import BaseDB
from pathlib import Path



class FileSystem(BaseDB):
    def __init__(self, exp_dir, db_name='.ndi'):
        self.exp_dir = Path(exp_dir)
        self.db_dir = self.exp_dir / db_name

        # Initializing FS Database
        if self.exp_dir.exists() and self.exp_dir.is_dir():
            self._create_collections()
        else:
            raise FileNotFoundError(
                f'No such file or directory: \'{self.exp_dir}\'')

    def add_experiment(self, experiment):
        self._collections[type(experiment)].add(experiment)
        for daq_system in experiment.daq_systems:
            self._collections[type(daq_system)].add(daq_system)
            daqreader = daq_system.daq_reader()

            for collection in ['probes', 'epochs', 'channels']:
                for ndi_object in getattr(daqreader, f'get_{collection}')():
                    self._collections[type(ndi_object)].add(ndi_object)

    def _create_collections(self):
        for collection in self._collections:
            self.create_collection(collection)

    def create_collection(self, ndi_class):
        self._collections[ndi_class] = Collection(
            self.db_dir / f'{ndi_class.__name__.lower()}s')

    def add(self, ndi_object):
        self._collections[type(ndi_object)].add(ndi_object)

    def find(self, ndi_class, **kwargs):
        ndi_objects = self._collections[ndi_class].find(ndi_class)

        if not kwargs:
            return ndi_objects

        return [
            ndi_object
            for ndi_object in ndi_objects
            for key, value in kwargs.items()
            if getattr(ndi_object, key) == value
        ]

    def find_by_id(self, ndi_class, id_):
        return self._collections[ndi_class].find_by_id(ndi_class, id_)

    def update(self):
        pass

    def update_by_id(self):
        pass

    def upsert(self, ndi_object):
        pass

    def delete(self, ndi_class, **kwargs):
        ids = [
            ndi_object.id
            for ndi_object in self.find(ndi_class, **kwargs)
        ]

        self._collections[ndi_class].delete(ids)

    def delete_by_id(self, ndi_class, id_):
        self._collections[ndi_class].delete_by_id(id_)


class Collection:
    def __init__(self, collection_dir):
        self.collection_dir = Path(collection_dir)

        # Initializing Collection
        self.collection_dir.mkdir(parents=True, exist_ok=True)

    def add(self, ndi_object):
        (self.collection_dir /
         f'{ndi_object.id}.dat').write_bytes(ndi_object.serialize())

    def find_by_id(self, ndi_class, id_):
        return ndi_class.from_flatbuffer((self.collection_dir / f'{id_}.dat').read_bytes())

    def find(self, ndi_class):
        return [
            ndi_class.from_flatbuffer(file.read_bytes())
            for file in self.collection_dir.glob('*.dat')
        ]

    def delete_by_id(self, id_):
        (self.collection_dir / f'{id_}.dat').unlink()

    def delete(self, ids):
        for id_ in ids:
            (self.collection_dir / f'{id_}.dat').unlink()
