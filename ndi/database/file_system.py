from .base_db import BaseDB
from pathlib import Path
from .utils import handle_iter, check_ndi_object, check_ndi_class
from ..database.query import AndQuery, OrQuery
import re
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

    def find(self, ndi_class, query=None):
        """Extracts all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.base_db`
        :param ndi_query: See :term:`NDI query`, defaults to find-all
        :type query: dict, optional
        :rtype: List<:term:`NDI object`>
        """
        return self._collections[ndi_class].find(query)

    def update_many(self, ndi_class, query=None, payload={}):
        """Updates all documents matching the given :term:`NDI query` in the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.base_db`
        :param ndi_query: See :term:`NDI query`, defaults to update-all
        :type query: dict, optional
        :param payload: Field and update values to be updated, defaults to {}
        :type payload: :term:`payload`, optional
        """
        self._collections[ndi_class].update_many(query, payload)

    def delete_many(self, ndi_class, query=None):
        """Deletes all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        .. currentmodule:: ndi.base_db
        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`BaseDB`
        :param ndi_query: See :term:`NDI query`, defaults to {}
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
    """Collection class for File System database
    """
    def __init__(self, db_dir, ndi_class):
        """Initializes a collection
        
        :param db_dir: Path to create new collection directory
        :type db_dir: str
        :param ndi_class: Any subclass of :class:`NDI_Object`
        :type ndi_class: type
        """
        self.collection_dir = Path(db_dir / f'{ndi_class.__name__.lower()}s',)
        self.ndi_class = ndi_class

        # Initializing Collection
        self.collection_dir.mkdir(parents=True, exist_ok=True)

    @handle_iter
    @check_ndi_class
    def add(self, ndi_object):
        """Takes any :term:`NDI object`\ (s) that is an instance of this collection's :term:`NDI class` and adds them to the database.

        :param ndi_object: The object(s) to be added to the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        file_path = self.collection_dir / f'{ndi_object.id}.dat'
        if not file_path.exists():
            self.upsert(ndi_object)
        else:
            raise FileExistsError(f'File \'{file_path}\' already exists')

    @handle_iter
    @check_ndi_class
    def update(self, ndi_object):
        """Takes any :term:`NDI object`\ (s) that is an instance of this collection's :term:`NDI class` and updates their :term:`document` in the database.

        :param ndi_object: The object(s) to be updated in the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        file_path = self.collection_dir / f'{ndi_object.id}.dat'
        if file_path.exists():
            self.upsert(ndi_object)
        else:
            raise FileNotFoundError(f'File \'{file_path}\' does not exist')

    @handle_iter
    @check_ndi_class
    def upsert(self, ndi_object):
        """Takes any :term:`NDI object`\ (s) that is an instance of this collection's :term:`NDI class` and updates their :term:`document` in the database. If an object doesn't have a document representation, it is added to the collection.

        :param ndi_object: The object(s) to be upserted into the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        (self.collection_dir /
         f'{ndi_object.id}.dat').write_bytes(ndi_object.serialize())

    @handle_iter
    @check_ndi_class
    def delete(self, ndi_object):
        """Takes any :term:`NDI object`\ (s) that is an instance of this collection's :term:`NDI class` and deletes their :term:`document` in the database.

        :param ndi_object: The object(s) to be removed from the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self.delete_by_id(ndi_object.id)

    def find(self, ndi_query={}):
        """Extracts all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        :param ndi_query: Not passing a query will return all :term:`document`s from the :term:`collection`.
        :type ndi_query: :term:`NDI query`, optional
        :rtype: List<:term:`NDI object`>
        """
        ndi_objects = [
            self.ndi_class.from_flatbuffer(file.read_bytes())
            for file in self.collection_dir.glob('*.dat')
        ]

        if not ndi_query:
            return ndi_objects

        return [
            ndi_object
            for ndi_object in ndi_objects
            if self.__parse_query(self.__Operator(ndi_object), ndi_query)
        ]

    def update_many(self, ndi_query={}, payload={}):
        """Updates all documents matching the given :term:`NDI query` in the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        :param ndi_query: Not passing a query will update all :term:`document`s from the :term:`collection.
        :type query: :term:`NDI query`, optional
        :param payload: Field and update values to be updated, defaults to {}. Not passing a :term:`payload` will result in no updates.
        :type payload: :term:`payload`, optional
        """
        ndi_objects = self.find(ndi_query)
        for ndi_object in ndi_objects:
            for key, value in payload.items():
                setattr(ndi_object, key, value)
        self.update(ndi_objects)

    def delete_many(self, ndi_query={}):
        """Deletes all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        :param ndi_query: Not passing a query will delete all :term:`document`s from the :term:`collection.
        :type query: :term:`payload`, optional
        """
        ndi_objects = self.find(ndi_query)
        self.delete(ndi_objects)

    def find_by_id(self, id_):
        """Retrieves the :term:`NDI object` with the given id from the specified :term:`collection`.

        :param id_: The identifier of the :term:`document` to extract.
        :type id_: str
        :rtype: :term:`NDI object`
        """
        return self.ndi_class.from_flatbuffer((self.collection_dir / f'{id_}.dat').read_bytes())

    def update_by_id(self, id_, payload={}):
        """Updates the :term:`NDI object` with the given id from the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        :param id_: The identifier of the :term:`document` to update.
        :type id_: str
        :param payload: Field and update values to be updated, defaults to {}. Not passing a :term:`payload` will result in no updates.
        :type payload: :term:`payload`, optional
        """
        ndi_object = self.find_by_id(id_)
        for key, value in payload.items():
            setattr(ndi_object, key, value)
        self.update(ndi_object)

    def delete_by_id(self, id_):
        """Deletes the :term:`NDI object` with the given id from the specified :term:`collection`.

        :param id_: The identifier of the :term:`document` to delete.
        :type id_: str
        """
        (self.collection_dir / f'{id_}.dat').unlink()

    def __parse_query(self, operator_object, ndi_query):
        if isinstance(ndi_query, AndQuery):
            return self.__and_query(operator_object, ndi_query)
        elif isinstance(ndi_query, OrQuery):
            return self.__or_query(operator_object, ndi_query)
        else:
            return self.__test_query(operator_object, ndi_query)

    @staticmethod
    def __test_query(operator_object, ndi_query):
        field, operator, value = ndi_query()
        return getattr(operator_object, operator)(field, value)
    
    def __and_query(self, operator_object, and_query):
        return all([
            self.__parse_query(operator_object, query) for query in and_query
        ])
    
    def __or_query(self, operator_object, or_query):
        return any([
            self.__parse_query(operator_object, query) for query in or_query
        ])

    class __Operator:
        def __init__(self, ndi_object):
            self.object = ndi_object

        def equals(self, field, value):
            return getattr(self.object, field) == value

        def not_equals(self, field, value):
            return getattr(self.object, field) != value

        def contains(self, field, value):
            return value in getattr(self.object, field)

        def match(self, field, value):
            return re.match(value, getattr(self.object, field))

        def greater_than(self, field, value):
            return getattr(self.object, field) > value

        def greater_than_or_equal_to(self, field, value):
            return getattr(self.object, field) >= value
        
        def less_than(self, field, value):
            return getattr(self.object, field) < value

        def less_than_or_equal_to(self, field, value):
            return getattr(self.object, field) <= value
        
        def exists(self, field, value):
            return hasattr(self.object, field) == value
        
        def in_(self, field, value):
            return getattr(self.object, field) in value
