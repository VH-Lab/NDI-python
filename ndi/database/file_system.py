from __future__ import annotations
from .ndi_database import NDI_Database
from pathlib import Path
from ..document import Document
from .query import CompositeQuery, AndQuery, OrQuery
import ndi.types as T
import re
import numpy as np


class FileSystem:
    """File system database API.

    .. currentmodule:: ndi.database.ndi_database

    Inherits from the :class:`NDI_Database` abstract class.
    """

    def __init__(self, exp_dir, db_name='.ndi'):
        self.exp_dir = Path(exp_dir)
        self.db_dir = self.exp_dir / db_name / 'documents'

        # Initializing FS Database
        if self.exp_dir.exists() and self.exp_dir.is_dir():
            self.lookup_dir = LookupCollection(self.db_dir, 'document')
            self.binary_dir = BinaryCollection(self.db_dir, 'document')
            self.db_dir.mkdir(parents=True, exist_ok=True)
        else:
            raise FileNotFoundError(
                f'No such file or directory: \'{self.exp_dir}\'')

    def add(self, ndi_document):
        file_path = self.db_dir / f'{ndi_document.id}.dat'
        if not file_path.exists():
            self.__verify_dependencies(ndi_document)
            self.upsert(ndi_document)
            self.__add_relationships(ndi_document)
        else:
            raise FileExistsError(f'File \'{file_path}\' already exists')

    def update(self, ndi_document):
        file_path = self.db_dir / f'{ndi_document.id}.dat'
        if file_path.exists():
            ndi_document._save_updates()
            self.upsert(ndi_document)
        else:
            raise FileNotFoundError(f'File \'{file_path}\' does not exist')

    def upsert(self, ndi_document):
        (self.db_dir /
         f'{ndi_document.id}.dat').write_bytes(ndi_document.serialize())

    def delete(self, ndi_document):
        self.delete_by_id(ndi_document.id)

    def find(self, ndi_query=None):
        ndi_documents = [
            Document.from_flatbuffer(file.read_bytes())
            for file in self.db_dir.glob('*.dat')
        ]

        if ndi_query is None:
            return ndi_documents

        return [
            ndi_document
            for ndi_document in ndi_documents
            if self.__parse_query(ndi_document.data, ndi_query)
        ]

    def update_many(self, ndi_query=None, payload={}):
        ndi_documents = self.find(ndi_query)
        for ndi_document in ndi_documents:
            self.__update(ndi_document, payload)

    def delete_many(self, ndi_query=None):
        ndi_documents = self.find(ndi_query)
        for ndi_document in ndi_documents:
            self.delete(ndi_document)

    def find_by_id(self, id_):
        return Document.from_flatbuffer((self.db_dir / f'{id_}.dat').read_bytes())

    def update_by_id(self, id_, payload={}):
        ndi_document = self.find_by_id(id_)
        self.__update(ndi_document, payload)

    def __update(self, ndi_document, payload):
        for key, value in payload.items():
            if key in ndi_document.data:
                ndi_document.data[key] = value
                self.update(ndi_document)

    def delete_by_id(self, id_):
        self.__delete_dependents(id_)
        (self.db_dir / f'{id_}.dat').unlink()

    # Query Parsing Methods
    def __parse_query(self, data, ndi_query):
        if isinstance(ndi_query, CompositeQuery):
            return self.__composite_query(data, ndi_query)
        return self.__test_query(data, ndi_query)

    def __test_query(self, data, ndi_query):
        field, operator, value = ndi_query()
        try:
            for key in field.split('.'):
                data = data[key]
            if operator == 'exists':
                return True == value
            return self.__operations[operator](data, value)
        except KeyError:
            if operator == 'exists':
                return False == value
            return False

    def __composite_query(self, data, ndi_query):
        return self.__operations[type(ndi_query)]([self.__parse_query(data, query) for query in ndi_query])

    __operations = {
        AndQuery: all,
        OrQuery: any,
        '==': lambda data, value: data == value,
        '!=': lambda data, value: data != value,
        'contains': lambda data, value: value in data,
        'match': lambda data, value: re.match(value, data),
        '>': lambda data, value: data > value,
        '>=': lambda data, value: data >= value,
        '<': lambda data, value: data < value,
        '<=': lambda data, value: data <= value,
        'in': lambda data, value: data in value
    }

    def get_dependencies(self, ndi_document):
        for key, value in ndi_document.data['_dependencies'].items():
            ndi_document.data['_dependencies'][key] = self.find_by_id(value)

    def __verify_dependencies(self, ndi_document):
        return all([
            self.find_by_id(value)
            for value in ndi_document.data['_dependencies'].values()
        ])

    def __add_relationships(self, ndi_document):
        for value in ndi_document.data['_dependencies'].values():
            self.lookup_dir.add(ndi_document.id, value)

    def __delete_dependents(self, id_):
        for dependent in self.lookup_dir.find_dependents(id_):
            self.__delete_dependents(dependent)
            (self.db_dir / f'{dependent}.dat').unlink()
            self.lookup_dir.remove(dependent, id_)

    def binary_write(self, ndi_document, data):
        self.binary_dir.write(ndi_document.id, data)

    def binary_read(self, ndi_document, start=0, end=-1):
        return self.binary_dir.read(ndi_document.id, start, end)


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

    def remove(self, ndi_document_id: T.NdiId, dependency_id: T.NdiId) -> None:
        """Remove a document relation from the collection

        :param ndi_document_id: [description]
        :type ndi_document_id: T.NdiId
        :param dependency_id: [description]
        :type dependency_id: T.NdiId
        """
        (self.collection_dir / f'{ndi_document_id}:{dependency_id}').unlink()

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


class BinaryCollection:
    def __init__(self, db_dir, name):
        self.collection_dir = Path(db_dir) / f'{name}_binary'

        # Initializing Collection
        self.collection_dir.mkdir(parents=True, exist_ok=True)

    def write(self, document_id, data):
        (self.collection_dir / f'{document_id}.bin').write_bytes(data.astype(float).tobytes())

    def write_stream(self, document_id):
        return self.FileStream(self.collection_dir / f'{document_id}.bin', 'wb')

    def read_slice(self, document_id, start=0, end=-1):
        with self.read_stream(document_id) as stream:
            stream.seek(start)
            return stream.read(end - start)

    def read_stream(self, document_id):
        return self.FileStream(self.collection_dir / f'{document_id}.bin', 'rb')

    class FileStream:
        def __init__(self, filepath, mode):
            self.filepath = filepath
            self.mode = mode

        def write(self, item):
            self.file.write(np.array([item]).astype(float).tobytes())

        def open(self):
            self.file = open(self.filepath, self.mode)
            return self

        def close(self):
            self.file.close()

        def seek(self, position):
            self.file.seek(position * 8)

        def read(self, size=-1):
            read_size = -1 if size < 0 else size * 8
            return np.frombuffer(self.file.read(read_size), dtype=float)

        def tell(self):
            return int(self.file.tell() / 8)

        def __enter__(self):
            return self.open()

        def __exit__(self, type, value, traceback):
            self.close()
