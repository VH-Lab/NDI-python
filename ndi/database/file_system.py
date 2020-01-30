from .base_db import BaseDB
from pathlib import Path
from .utils import check_ndi_object

class FileSystem(BaseDB):
    def __init__(self, exp_dir, db_name='.ndi'):
        self.exp_dir = Path(exp_dir)
        self.db_dir = self.exp_dir / db_name

        # Initializing FS Database
        if self.exp_dir.exists() and self.exp_dir.is_dir():
            self.__create_collections()
        else:
            raise FileNotFoundError(
                f'No such file or directory: \'{self.exp_dir}\'')

    @check_ndi_object
    def add_experiment(self, experiment):
        self._collections[type(experiment)].add(experiment)
        for daq_system in experiment.daq_systems:
            self._collections[type(daq_system)].add(daq_system)
            daqreader = daq_system.daq_reader()

            for collection in ['probes', 'epochs', 'channels']:
                self.add(getattr(daqreader, f'get_{collection}')())

    def __create_collections(self):
        for collection in self._collections:
            self.create_collection(collection)

    def create_collection(self, ndi_class):
        self._collections[ndi_class] = Collection(self.db_dir, ndi_class)

    @check_ndi_object
    def add(self, ndi_object):
        self._collections[type(ndi_object)].add(ndi_object)

    @check_ndi_object
    def update(self, ndi_object):
        self._collections[type(ndi_object)].update(ndi_object)

    @check_ndi_object
    def upsert(self, ndi_object):
        self._collections[type(ndi_object)].upsert(ndi_object)

    @check_ndi_object
    def delete(self, ndi_object):
        self._collections[type(ndi_object)].delete(ndi_object)

    def find(self, ndi_class, query={}):
        return self._collections[ndi_class].find(query)
    
    def update_many(self, ndi_class, query={}, payload={}):
        self._collections[ndi_class].update_many(query, payload)
    
    def delete_many(self, ndi_class, query={}):
        self._collections[ndi_class].delete_many(query)

    def find_by_id(self, ndi_class, id_):
        return self._collections[ndi_class].find_by_id(id_)

    def update_by_id(self, ndi_class, id_, payload={}):
        self._collections[ndi_class].update_by_id(id_, payload)

    def delete_by_id(self, ndi_class, id_):
        self._collections[ndi_class].delete_by_id(id_)


class Collection:
    def __init__(self, db_dir, ndi_class):
        self.collection_dir = Path(db_dir / f'{ndi_class.__name__.lower()}s',)
        self.ndi_class = ndi_class

        # Initializing Collection
        self.collection_dir.mkdir(parents=True, exist_ok=True)

    @check_ndi_object
    def add(self, ndi_object):
        file_path = self.collection_dir / f'{ndi_object.id}.dat'
        if not file_path.exists():
            self.upsert(ndi_object)
        else:
            raise FileExistsError(f'File \'{file_path}\' already exists')

    @check_ndi_object
    def update(self, ndi_object):
        file_path = self.collection_dir / f'{ndi_object.id}.dat'
        if file_path.exists():
            self.upsert(ndi_object)
        else:
            raise FileNotFoundError(f'File \'{file_path}\' does not exist')

    @check_ndi_object  
    def upsert(self, ndi_object):
        (self.collection_dir / f'{ndi_object.id}.dat').write_bytes(ndi_object.serialize())
    
    @check_ndi_object
    def delete(self, ndi_object):
        self.delete_by_id(ndi_object.id)

    def find(self, query={}):
        ndi_objects = [
            self.ndi_class.from_flatbuffer(file.read_bytes())
            for file in self.collection_dir.glob('*.dat')
        ]

        if not query:
            return ndi_objects

        return [
            ndi_object
            for ndi_object in ndi_objects
            for key, value in query.items()
            if getattr(ndi_object, key) == value
        ]

    def update_many(self, query={}, payload={}):
        ndi_objects = self.find(query)
        for ndi_object in ndi_objects:
            for key, value in payload.items():
                ndi_object.__dict__[key] = value
        self.update(ndi_objects)

    def delete_many(self, query={}):
        ndi_objects = self.find(query)
        self.delete(ndi_objects)

    def find_by_id(self, id_):
        return self.ndi_class.from_flatbuffer((self.collection_dir / f'{id_}.dat').read_bytes())

    def update_by_id(self, id_, payload={}):
        ndi_object = self.find_by_id(id_)
        for key, value in payload.items():
            ndi_object.__dict__[key] = value
        self.update(ndi_object)

    def delete_by_id(self, id_):
        (self.collection_dir / f'{id_}.dat').unlink()
