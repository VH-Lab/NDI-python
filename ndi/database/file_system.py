from __future__ import annotations
from .ndi_database import NDI_Database
from pathlib import Path
from ..document import Document
from ..decorators import handle_iter
from ..utils import class_to_collection_name
from .utils import check_ndi_object, check_ndi_class
from .query import CompositeQuery, AndQuery, OrQuery
import ndi.types as T
import re


class FileSystem(NDI_Database):
    """File system database API.

    .. currentmodule:: ndi.database.ndi_database

    Inherits from the :class:`NDI_Database` abstract class.
    """

    def __init__(self, exp_dir: T.FilePath, db_name: str = '.ndi', document_extensions=[]):
        """FileSystem constructor: initializes a named FileSystem instance and connects to it at the given path. If it doesn't already exist, it creates a new file system database at the given path.

        :param exp_dir: A path to the file system database directory.
        :type exp_dir: str
        :param db_name: defaults to '.ndi'
        :type db_name: str, optional
        :raises FileNotFoundError: [description]
        """

        self.exp_dir = Path(exp_dir)
        self.db_dir = self.exp_dir / db_name

        self._document_collections = {
            document_extension.__name__: document_extension
            for document_extension in document_extensions
        }

        for document_extension in document_extensions:
            self._collections[document_extension] = None

        # Initializing FS Database
        if self.exp_dir.exists() and self.exp_dir.is_dir():
            self.__create_collections()
        else:
            raise FileNotFoundError(
                f'No such file or directory: \'{self.exp_dir}\'')

    @handle_iter
    @check_ndi_object
    def add_experiment(self, experiment: T.Experiment) -> None:
        """.. currentmodule:: ndi.experiment

        Takes an :class:`Experiment` and adds it and it's contents (including its DaqSystems, Probes, Channels, and Epochs) to the file database.

        :param experiment: 
        :type experiment: :class:`Experiment`
        """
        self._collections[type(experiment)].add(
            experiment.id, experiment.serialize())
        for daq_system in experiment.daq_systems:
            self._collections[type(daq_system)].add(
                daq_system.id, daq_system.serialize())
            daq_reader = daq_system.daq_reader

            for collection in ['probes', 'epochs', 'channels']:
                self.add(getattr(daq_reader, f'get_{collection}')())

    def __create_collections(self) -> None:
        """
        .. currentmodule:: ndi.ndi_database:

        Build all :term:`collection`\ s from the _collections property on :class:`NDI_Database`.
        """
        for collection in self._collections:
            self.create_collection(collection)
        self._collections['document_lookup'] = LookupCollection(
            self.db_dir, 'document')

    def create_collection(self, ndi_class: T.NdiClass) -> None:
        """Instantiates a :term:`collection` from the given :term:`NDI class` using its properties to set the :term:`field`\ s. 

        :param ndi_class: The :term:`NDI class` that will define the new collection.
        :type ndi_class: :class:`NDI_Database`
        """
        self._collections[ndi_class] = Collection(self.db_dir, ndi_class)

    def drop_collection(self, ndi_class: T.NdiClass) -> None:
        """Deletes the :term:`collection` corresponding to the given :term:`NDI class`.

        :param ndi_class: The :term:`NDI class` whose corresponding collection will be deleted
        :type ndi_class: type
        """
        self._collections[ndi_class].drop()
        del self._collections[ndi_class]

    @handle_iter
    @check_ndi_object
    def add(self, ndi_object: T.NdiObject) -> None:
        """.. currentmodule:: ndi.ndi_database

        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and adds them to the database. Objects may belong to different :term:`NDI class`\ es.

        :param ndi_object: The object(s) to be added to the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self._collections[type(ndi_object)].add(
            ndi_object.id, ndi_object.serialize())
        if isinstance(ndi_object, Document):
            self.__add_document_dependencies(ndi_object)
            self.__add_document_extension(ndi_object)

    @handle_iter
    @check_ndi_object
    def update(self, ndi_object: T.NdiObject) -> None:
        """.. currentmodule:: ndi.ndi_database

        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. Objects may belong to different :term:`NDI class`\ es. 

        :param ndi_object: The object(s) to be updated in the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        if isinstance(ndi_object, Document):
            ndi_object._save_updates()
            self.add(ndi_object)
        else:
            self._collections[type(ndi_object)].update(ndi_object)

    @handle_iter
    @check_ndi_object
    def upsert(self, ndi_object: T.NdiObject) -> None:
        """.. currentmodule:: ndi.ndi_database

        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and updates their :term:`document` in the database. If an object doesn't have a document representation, it is added to the collection. Objects may belong to different :term:`NDI class`\ es. 

        :param ndi_object: The object(s) to be upserted into the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        if isinstance(ndi_object, Document):
            if self.find_by_id(Document, ndi_object.id):
                self.update(ndi_object)
            else:
                self.add(ndi_object)
        else:
            self._collections[type(ndi_object)].upsert(ndi_object)

    @handle_iter
    @check_ndi_object
    def delete(self, ndi_object: T.NdiObject) -> None:
        """.. currentmodule:: ndi.ndi_database

        Takes any :term:`NDI object`\ (s) with a :term:`collection` representation in the database and deletes their :term:`document` in the database. Objects may belong to different :term:`NDI class`\ es. 

        :param ndi_object: The object(s) to be removed from the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self._collections[type(ndi_object)].delete(ndi_object)

    def find(self, ndi_class: T.NdiClass, ndi_query: T.Optional[T.Query] = None) -> T.List[T.NdiObject]:
        """Extracts all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.ndi_database`
        :param ndi_query: See :term:`NDI query`, defaults to find-all
        :type query: dict, optional
        :rtype: List<:term:`NDI object`>
        """
        ndi_objects = self._collections[ndi_class].find(ndi_query)
        if ndi_class == Document:
            for ndi_document in ndi_objects:
                self.__get_document_dependencies(ndi_document)
                self.__get_document_extension(ndi_document)
        return ndi_objects

    def update_many(self, ndi_class: T.NdiClass, query: T.Optional[T.Query] = None, payload: dict = {}) -> None:
        """Updates all documents matching the given :term:`NDI query` in the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`ndi.ndi_database`
        :param ndi_query: See :term:`NDI query`, defaults to update-all
        :type query: dict, optional
        :param payload: Field and update values to be updated, defaults to {}
        :type payload: :term:`payload`, optional
        """
        self._collections[ndi_class].update_many(query, payload)

    def delete_many(self, ndi_class: T.NdiClass, query: T.Optional[T.Query] = None) -> None:
        """Deletes all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`NDI_Database`
        :param ndi_query: See :term:`NDI query`, defaults to {}
        :type query: dict, optional
        """
        self._collections[ndi_class].delete_many(query)

    def find_by_id(self, ndi_class: T.NdiClass, id_: T.Union[T.NdiId, str]) -> T.NdiObject:
        """Retrieves the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to search.
        :type ndi_class: :class:`NDI_Database`
        :param id_: The identifier of the :term:`document` to extract.
        :type id_: str
        :rtype: :term:`NDI object`
        """
        ndi_object = self._collections[ndi_class].find_by_id(id_)
        if ndi_class == Document:
            self.__get_document_dependencies(ndi_object)
            self.__get_document_extension(ndi_object)
        return ndi_object

    def update_by_id(self, ndi_class: T.NdiClass, id_: T.Union[T.NdiId, str], payload: dict = {}) -> None:
        """Updates the :term:`NDI object` with the given id from the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to update.
        :type ndi_class: :class:`NDI_Database`
        :param id_: The identifier of the :term:`document` to update.
        :type id_: str
        """
        self._collections[ndi_class].update_by_id(id_, payload)

    def delete_by_id(self, ndi_class: T.NdiClass, id_: T.Union[T.NdiId, str]) -> None:
        """Deletes the :term:`NDI object` with the given id from the specified :term:`collection`.

        .. currentmodule:: ndi.ndi_database

        :param ndi_class: The :term:`NDI class` that defines the :term:`collection` to query.
        :type ndi_class: :class:`NDI_Database`
        :param id_: The identifier of the :term:`document` to delete.
        :type id_: str
        """
        self._collections[ndi_class].delete_by_id(id_)

    def __add_document_dependencies(self, ndi_document: T.Document) -> None:
        for dependency_id in ndi_document.dependencies:
            if self.find_by_id(Document, dependency_id):
                self._collections['document_lookup'].add(
                    ndi_document.id, dependency_id)
            else:
                raise FileNotFoundError(
                    f'Cannot add document \'{dependency_id}\' as a dependency because it does not exist in the database')

    def __add_document_extension(self, ndi_document: T.Document) -> None:
        if doc_ext := ndi_document.document_extension:
            self._collections[type(doc_ext)].add(doc_ext.document_id, doc_ext.serialize())

    def __get_document_dependencies(self, ndi_document: T.Document) -> None:
        dependencies = self._collections['document_lookup'].find_dependencies(
            ndi_document.id)
        ndi_document.dependencies = dependencies

    def __get_document_extension(self, ndi_document: T.Document) -> None:
        try:
            doc_ext = self._collections[self._document_collections[ndi_document.document_type]].find_by_id(
                ndi_document.id)
            ndi_document.set_document_extension(doc_ext)
        except KeyError:
            pass


class Collection:
    """Collection class for File System database
    """

    def __init__(self, db_dir: Path, ndi_class: T.NdiClass) -> None:
        """Initializes a collection

        :param db_dir: Path to create new collection directory
        :type db_dir: str
        :param ndi_class: Any subclass of :class:`NDI_Object`
        :type ndi_class: type
        """
        self.collection_dir = Path(
            db_dir / class_to_collection_name(ndi_class))
        self.ndi_class = ndi_class

        # Initializing Collection
        self.collection_dir.mkdir(parents=True, exist_ok=True)

    def drop(self) -> None:
        """Deletes all entries in the collection and then deletes the directory
        """
        self.delete_many()
        self.collection_dir.rmdir()

    def add(self, id_: T.NdiId, flatbuffer: bytearray) -> None:
        """Takes any :term:`NDI object`\ (s) that is an instance of this collection's :term:`NDI class` and adds them to the database.

        :param ndi_object: The object(s) to be added to the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        file_path = self.collection_dir / f'{id_}.dat'
        if not file_path.exists():
            self.upsert(id_, flatbuffer)
        else:
            raise FileExistsError(f'File \'{file_path}\' already exists')

    def update(self, id_: T.NdiId, flatbuffer: bytearray) -> None:
        """Takes any :term:`NDI object`\ (s) that is an instance of this collection's :term:`NDI class` and updates their :term:`document` in the database.

        :param ndi_object: The object(s) to be updated in the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        file_path = self.collection_dir / f'{id_}.dat'
        if file_path.exists():
            self.upsert(id_, flatbuffer)
        else:
            raise FileNotFoundError(f'File \'{file_path}\' does not exist')

    def upsert(self, id_: T.NdiId, flatbuffer: bytearray) -> None:
        """Takes any :term:`NDI object`\ (s) that is an instance of this collection's :term:`NDI class` and updates their :term:`document` in the database. If an object doesn't have a document representation, it is added to the collection.

        :param ndi_object: The object(s) to be upserted into the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        (self.collection_dir / f'{id_}.dat').write_bytes(flatbuffer)

    @handle_iter
    @check_ndi_class
    def delete(self, ndi_object: T.NdiObject) -> None:
        """Takes any :term:`NDI object`\ (s) that is an instance of this collection's :term:`NDI class` and deletes their :term:`document` in the database.

        :param ndi_object: The object(s) to be removed from the database.
        :type ndi_object: List<:term:`NDI object`> | :term:`NDI object`
        """
        self.delete_by_id(ndi_object.id)

    def find(self, ndi_query: T.Optional[T.Query] = None) -> T.List[T.NdiObject]:
        """Extracts all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        :param ndi_query: Not passing a query will return all :term:`document`\ s from the :term:`collection`.
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
            if self.__parse_query(ndi_object, ndi_query)
        ]

    def update_many(self, ndi_query: T.Optional[T.Query] = None, payload: dict = {}) -> None:
        """Updates all documents matching the given :term:`NDI query` in the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        :param ndi_query: Not passing a query will update all :term:`document`\ s from the :term:`collection.
        :type query: :term:`NDI query`, optional
        :param payload: Field and update values to be updated, defaults to {}. Not passing a :term:`payload` will result in no updates.
        :type payload: :term:`payload`, optional
        """
        ndi_objects = self.find(ndi_query)
        for ndi_object in ndi_objects:
            for key, value in payload.items():
                setattr(ndi_object, key, value)
            self.update(ndi_object.id, ndi_object.serialize())

    def delete_many(self, ndi_query: T.Optional[T.Query] = None) -> None:
        """Deletes all documents matching the given :term:`NDI query` in the specified :term:`collection`.

        :param ndi_query: Not passing a query will delete all :term:`document`\ s from the :term:`collection.
        :type query: :term:`payload`, optional
        """
        ndi_objects = self.find(ndi_query)
        self.delete(ndi_objects)

    def find_by_id(self, id_: T.Union[T.NdiId, str]) -> T.Optional[T.NdiObject]:
        """Retrieves the :term:`NDI object` with the given id from the specified :term:`collection`.

        :param id_: The identifier of the :term:`document` to extract.
        :type id_: str
        :rtype: :term:`NDI object`
        """
        try:
            return self.ndi_class.from_flatbuffer((self.collection_dir / f'{id_}.dat').read_bytes())
        except FileNotFoundError:
            return None

    def update_by_id(self, id_: T.Union[T.NdiId, str], payload: dict = {}) -> None:
        """Updates the :term:`NDI object` with the given id from the specified :term:`collection` with the fields/values in the :term:`payload`. Fields that aren't included in the payload are not touched.

        :param id_: The identifier of the :term:`document` to update.
        :type id_: str
        :param payload: Field and update values to be updated, defaults to {}. Not passing a :term:`payload` will result in no updates.
        :type payload: :term:`payload`, optional
        """
        ndi_object = self.find_by_id(id_)
        for key, value in payload.items():
            setattr(ndi_object, key, value)
        self.update(ndi_object.id, ndi_object.serialize())

    def delete_by_id(self, id_: T.Union[T.NdiId, str]) -> None:
        """Deletes the :term:`NDI object` with the given id from the specified :term:`collection`.

        :param id_: The identifier of the :term:`document` to delete.
        :type id_: str
        """
        (self.collection_dir / f'{id_}.dat').unlink()

    # Query Parsing Methods
    def __parse_query(self, ndi_object: T.NdiObject, ndi_query: T.Query) -> bool:
        if isinstance(ndi_query, CompositeQuery):
            return self.__operations[type(ndi_query)]([self.__parse_query(ndi_object, query) for query in ndi_query])
        field, operator, value = ndi_query.query
        return self.__operations[operator](ndi_object, field, value)

    __operations: T.Dict[T.Union[T.NdiQueryClass, str], T.Callable] = {
        AndQuery: all,
        OrQuery: any,
        '==': lambda ndi_object, field, value: getattr(ndi_object, field) == value,
        '!=': lambda ndi_object, field, value: getattr(ndi_object, field) != value,
        'contains': lambda ndi_object, field, value: value in getattr(ndi_object, field),
        'match': lambda ndi_object, field, value: re.match(value, getattr(ndi_object, field)),
        '>': lambda ndi_object, field, value: getattr(ndi_object, field) > value,
        '>=': lambda ndi_object, field, value: getattr(ndi_object, field) >= value,
        '<': lambda ndi_object, field, value: getattr(ndi_object, field) < value,
        '<=': lambda ndi_object, field, value: getattr(ndi_object, field) <= value,
        'exists': lambda ndi_object, field, value: hasattr(ndi_object, field) == value,
        'in': lambda ndi_object, field, value: getattr(ndi_object, field) in value
    }


class LookupCollection:
    """Collection class for File System lookups
    """
    def __init__(self, db_dir: Path, name: str) -> None:
        """Initializes a lookup collection

        :param db_dir: [description]
        :type db_dir: Path
        :param name: Name of the lookup collection. Will be appended with "_lookup"
        :type name: str
        """
        self.collection_dir = Path(db_dir) / f'{name}_lookup'

        # Initializing Collection
        self.collection_dir.mkdir(parents=True, exist_ok=True)

    def add(self, ndi_document_id: T.NdiId, dependency_id: T.NdiId) -> None:
        """Add a document relation to the collection 
        
        :param ndi_document_id: [description]
        :type ndi_document_id: T.NdiId
        :param dependency_id: [description]
        :type dependency_id: T.NdiId
        """
        (self.collection_dir /
         f'{ndi_document_id}:{dependency_id}').touch(exist_ok=False)

    def find_dependencies(self, dependent_id: T.NdiId) -> T.List[str]:
        """Find dependencies given a dependent's id
        
        :param dependent_id: [description]
        :type dependent_id: T.NdiId
        :return: [description]
        :rtype: T.List[str]
        """
        return self.__find(dependent_id, 0)

    def find_dependents(self, dependency_id: T.NdiId) -> T.List[str]:
        """Find dependents given a dependency's id
        
        :param dependency_id: [description]
        :type dependency_id: T.NdiId
        :return: [description]
        :rtype: T.List[str]
        """
        return self.__find(dependency_id, 1)

    def __find(self, id_: T.NdiId, index: int) -> T.List[str]:
        ids = []
        for row in self.collection_dir.iterdir():
            split = row.stem.split(':')
            if id_ == split[index]:
                ids.append(split[1 - index])
        return ids
