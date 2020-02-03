from .base_db import BaseDB
from pathlib import Path
from .utils import handle_iter, check_ndi_object

class FileSystem(BaseDB):
    """File system database API.
    
    .. currentmodule:: ndi.database.base_db
    Inherits from the :class:`BaseDB` abstract class.
    """
    def __init__(self, exp_dir, db_name='.ndi'):
        """FileSystem constructor: initializes a named FileSystem instance and connects to it at the given path. If it doesn't already exist, it creates a new file system database at the given path.
        
        :param exp_dir: A path to the file system database directory.
        :type exp_dir: str
        :param db_name: defaults to '.ndi'
        :type db_name: str, optional
        :raises FileNotFoundError: [description]
        """

        self.exp_dir = Path(exp_dir)
        self.db_dir = self.exp_dir / db_name

        # Initializing FS Database
        if self.exp_dir.exists() and self.exp_dir.is_dir():
            self.__create_collections()
        else:
            raise FileNotFoundError(
                f'No such file or directory: \'{self.exp_dir}\'')

    @handle_iter
    @check_ndi_object
    def add_experiment(self, experiment):
        """.. currentmodule:: ndi.experiment
        Takes an :class:`Experiment` and adds it and it's contents (including its DaqSystems, Probes, Channels, and Epochs) to the file database.

        :param experiment: 
        :type experiment: :class:`Experiment`
        """
        # TODO: handle List[experiment]
        self._collections[type(experiment)].add(experiment)
        for daq_system in experiment.daq_systems:
            self._collections[type(daq_system)].add(daq_system)
            daqreader = daq_system.daq_reader()

            for collection in ['probes', 'epochs', 'channels']:
                self.add(getattr(daqreader, f'get_{collection}')())

    def __create_collections(self):
        """.. currentmodule:: ndi.base_db:
        Build all :term:`collection`s from the _collections property on :class:`BaseDB`.
        """
        for collection in self._collections:
            self.create_collection(collection)

    def create_collection(self, ndi_class):
        """Instantiates a :term:`collection` from the given :term:`NDI class` using its properties to set the :term:`field`s. 
        
        :param ndi_class: The :term:`NDI class` that will define the new collection.
        :type ndi_class: :class:`BaseDB`
        """
        self._collections[ndi_class] = Collection(self.db_dir, ndi_class)

    @handle_iter
    @check_ndi_object
    def add(self, ndi_object):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and adds them to the database. Objects may belong to different :term:`NDI classes`.
        
        :param ndi_object: The object(s) to be added to the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self._collections[type(ndi_object)].add(ndi_object)

    @handle_iter
    @check_ndi_object
    def update(self, ndi_object):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. Objects may belong to different :term:`NDI classes`. 
        
        :param ndi_object: The object(s) to be updated in the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self._collections[type(ndi_object)].update(ndi_object)

    @handle_iter
    @check_ndi_object
    def upsert(self, ndi_object):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. If an object doesn't have a document representation, it is added to the collection. Objects may belong to different :term:`NDI classes`. 
        
        :param ndi_object: The object(s) to be upserted into the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self._collections[type(ndi_object)].upsert(ndi_object)

    @handle_iter
    @check_ndi_object
    def delete(self, ndi_object):
        """.. currentmodule:: ndi.base_db
        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and deletes their :term:`document` in the database. Objects may belong to different :term:`NDI classes`. 
        
        :param ndi_object: The object(s) to be removed from the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self._collections[type(ndi_object)].delete(ndi_object)

    def find(self, ndi_class, query={}):
        """Extracts all documents matching the given :term:`query` in the specified :term:`collection`.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.base_db`
        :param query: See :term:`query`, defaults to find-all
        :type query: dict, optional
        :rtype: List<:term:`NDI object`>
        """
        return self._collections[ndi_class].find(query)
    
    def update_many(self, ndi_class, query={}, payload={}):
        """Updates all documents matching the given :term:`query` in the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.base_db`
        :param query: See :term:`query`, defaults to update-all
        :type query: dict, optional
        :param payload: Field and update values to be updated, defaults to {}
        :type payload: :term:`payload`, optional
        """
        self._collections[ndi_class].update_many(query, payload)
    
    def delete_many(self, ndi_class, query={}):
        """Deletes all documents matching the given :term:`query` in the specified :term:`collection`.
        
        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`BaseDB`
        :param query: See :term:`query`, defaults to {}
        :type query: dict, optional
        """
        self._collections[ndi_class].delete_many(query)

    def find_by_id(self, ndi_class, id_):
        """Retrieves the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to search.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to extract.
        :type id_: str
        :rtype: :term:`NDI object`
        """
        return self._collections[ndi_class].find_by_id(id_)

    def update_by_id(self, ndi_class, id_, payload={}):
        """Updates the :term:`NDI object` with the given id from the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to update.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to update.
        :type id_: str
        """
        self._collections[ndi_class].update_by_id(id_, payload)

    def delete_by_id(self, ndi_class, id_):
        """Deletes the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`BaseDB`
        :param id_: The identifier of the :term:`document` to delete.
        :type id_: str
        """
        self._collections[ndi_class].delete_by_id(id_)


class Collection:
    def __init__(self, db_dir, ndi_class):
        self.collection_dir = Path(db_dir / f'{ndi_class.__name__.lower()}s',)
        self.ndi_class = ndi_class

        # Initializing Collection
        self.collection_dir.mkdir(parents=True, exist_ok=True)

    @handle_iter
    @check_ndi_object
    def add(self, ndi_object):
        file_path = self.collection_dir / f'{ndi_object.id}.dat'
        if not file_path.exists():
            self.upsert(ndi_object)
        else:
            raise FileExistsError(f'File \'{file_path}\' already exists')

    @handle_iter
    @check_ndi_object
    def update(self, ndi_object):
        file_path = self.collection_dir / f'{ndi_object.id}.dat'
        if file_path.exists():
            self.upsert(ndi_object)
        else:
            raise FileNotFoundError(f'File \'{file_path}\' does not exist')

    @handle_iter
    @check_ndi_object  
    def upsert(self, ndi_object):
        (self.collection_dir / f'{ndi_object.id}.dat').write_bytes(ndi_object.serialize())
    
    @handle_iter
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
