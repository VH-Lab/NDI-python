from __future__ import annotations
import ndi.types as T
from .schema import Document as build_document
import json
from .flatbuffer_object import Flatbuffer_Object
from .context import Context
from did.time import current_time
from did import Query as Q
from contextlib import contextmanager

class BinaryWrapper:
    def __init__(self, binary_collection: T.BinaryCollection = None, id_: str =''):
        self.id = id_
        self.binary_collection = binary_collection
    
    def connect(self, binary_collection: T.BinaryCollection = None):
        self.binary_collection = binary_collection

    def open_write_stream(self):
        return self.binary_collection.open_write_stream(self.id)

    def open_read_stream(self):
        return self.binary_collection.open_read_stream(self.id)



class Document(Flatbuffer_Object):
    """
    A flatbuffer interface for documents.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    def __init__(self, data: dict = {}, name: str = '', session_id: str = '', id_=None):
        """Creates new ndi_document

        :param id_: [description], defaults to None
        :type id_: T.NdiId, optional
        :param data: [description], defaults to None
        :type data: dict, optional
        """
        super().__init__(id_)
        self.ctx = Context()
        self.binary = BinaryWrapper()
        self.binary.id = self.id
        self.data = data or {
            'depends_on': [],
            'dependencies': [],
            'binary_files': [],
            'base': {
                'id': self.id,
                'session_id': session_id,
                'name': name,
                'datestamp': current_time(),
                'snapshots': [],
                'records': [],
            },
            'document_class': {
                'definition': None,
                'validation': None,
                'name': None,
                'property_list_name': None,
                'class_version': None,
                'superclasses': [],
            },
        }
        if data:
            if data['base']['id']:
                self.id = data['base']['id']
            else:
                data['base']['id'] = self.id
        self.deleted = False
        self.__dependencies = []
        self.__depends_on = []

    @property
    def current(self):
        return self.refresh()
    
    def at_snapshot(self, snapshot):
        return self.refresh(snapshot=snapshot)
    
    def at_commit(self, commit):
        return self.refresh(commit=commit)
        
    @property
    def version(self):
        try:
            return self.base['records'][0]
        except IndexError:
            return None
        
    @property
    def snapshot(self):
        try:
            return self.base['snapshots'][0]
        except IndexError:
            return None

    @property
    def base(self):
        return self.data['base']

    @base.setter
    def base(self, value):
        self.data['base'] = value

    @property
    def class_(self):
        return self.data['document_class']

    @class_.setter
    def class_(self, value):
        self.data['document_class'] = value

    @property
    def dependencies(self):
        if not self.__dependencies:
            self.__dependencies = self.get_dependencies()
        return self.__dependencies

    @dependencies.setter
    def dependencies(self, value):
        self.__dependencies = value

    @property
    def depends_on(self):
        if not self.__depends_on:
            self.__depends_on = self.get_depends_on()
        return self.__depends_on

    @depends_on.setter
    def depends_on(self, value):
        self.__depends_on = value

    @property
    def dependencies_metadata(self):
        return self.data['dependencies']

    @dependencies_metadata.setter
    def dependencies_metadata(self, dependencies):
        self.data['dependencies'] = dependencies

    @property
    def depends_on_metadata(self):
        return self.data['depends_on']
    @depends_on_metadata.setter
    def depends_on_metadata(self, depends_on):
        self.data['depends_on'] = depends_on
    
    def set_ctx_database(self, database: T.NdiDatabase) -> None:
        self.ctx.data_interface_database = database

    def with_ctx_database(self, database: T.NdiDatabase) -> T.Document:
        self.ctx.data_interface_database = database
        return self

    def set_ctx(self, ctx: T.Context) -> None:
        self.ctx = ctx
        self.binary.connect(self.ctx.bin)

    def with_ctx(self, ctx: T.Context) -> T.Document:
        self.set_ctx(ctx)
        return self

    def _connect_binary_fork(self, binary_collection):
        self.binary = BinaryWrapper(binary_collection, self.id)

    @contextmanager
    def available_ctx(self) -> T.Generator:
        if not self.ctx:
            """Will fire if the document is not in the database (ctx is attached any time a document is added or retrieved from the database; only user-initialized Documents should not have a ctx)."""
            # TODO: make this error message more helpful when ctx is well defined
            raise RuntimeError('This document is not attached to a database.')
        else:
            yield

    def save(self):
        """Saves staged changes to database."""
        with self.available_ctx():
            self.ctx.db.save()

    def update(self, save=None):
        """
        Stages document data update.
        """
        with self.available_ctx():
            self.ctx.db.update(self, save=save)

    def upsert(self, save=None):
        """
        Stages document data upsert.
        """
        with self.available_ctx():
            self.ctx.db.upsert(self, save=save)

    def refresh(self, snapshot=None, commit=None):
        self_in_db = self.ctx.db.find_by_id(self.id, snapshot, commit)
        try:
            self.data = self_in_db.data
        except AttributeError:
            self._clear_own_data()
        return self

    def get_history(self):
        """Version history relevant to this document. 

        :return: Lists, from newest to oldest, the document's (database_snapshot_id, version_hash) for each change made to the document.
        :rtype: List[Tuple]
        """
        return zip(self.base['snapshots'], self.base['records'])


    def __check_dependency_name_exists(self, name: str):
        dependencies = self.dependencies_metadata
        return any([name == dep['name'] for dep in dependencies])

    def __check_dependency_id_exists(self, id_: str):
        return any([id_ == dep['id'] for dep in self.dependencies_metadata])
    
    def __format_dep(self, ndi_document, related_document, name=None):
        """Formats depends_on and dependencies objects."""
        return {
            'name': name or ndi_document.data['base']['name'] or ndi_document.id,
            'id': related_document.id,
            'record': related_document.version,
            'snapshot': related_document.snapshot,
            'own_record': ndi_document.version, 
        }

    def add_dependency(self, ndi_document: T.Document, name: str = None, save=None):
        name = name or ndi_document.data['base']['name'] or ndi_document.id
        self.__verify_dependency(ndi_document, name)
        self.ctx.db.add(ndi_document, save=False)
        self.__link_dependency(ndi_document, name)
        self.ctx.db.update(self, save=False)
        ndi_document.with_ctx(self.ctx)
        if save:
            self.ctx.db.save()
    
    def link_dependency(self, ndi_document: T.Document, name: str = None):
        name = name or ndi_document.data['base']['name'] or ndi_document.id
        self.__verify_dependency(ndi_document, name)

        self.__link_dependency(ndi_document, name)

    def __verify_dependency(self, ndi_document, name):
        if self.__check_dependency_name_exists(name):
            raise RuntimeError(
                'Dependency name is already in use (dependency names default to the document name if not specified).')
        elif self.__check_dependency_id_exists(ndi_document.id):
            dependency_name = ndi_document.base['name']
            own_name = self.base['name']
            raise RuntimeError(
                f'Document {dependency_name} is already a dependency of document {own_name}.')

    def __link_dependency(self, ndi_document, name):
        ndi_document.depends_on_metadata.append(self.__format_dep(ndi_document, self))
        new_dependency = self.__format_dep(self, ndi_document, name)
        self.dependencies_metadata = [
            *self.dependencies_metadata, 
            new_dependency 
        ]
        return ndi_document

    def get_dependencies(self):
        dependencies = {}
        for dependency in self.dependencies_metadata:
            dependencies[dependency['name']] = self.ctx.db.find_record(dependency['record'])
        return dependencies

    def get_depends_on(self):
        depends_on = {}
        for dep in self.depends_on_metadata:
            depends_on[dep['name']] = self.ctx.db.find_record(dep['record'])
        return depends_on


    def delete(self, remove_history=False, save=None):
        deletees = self.get_dependencies()
        if remove_history:
            deletees.extend(self.get_history())
        for ndi_document in deletees:
            ndi_document.delete(remove_history=remove_history, save=False)
        self._remove_self_from_dependencies()
        self.ctx.db.delete(self, save=False)
        self._clear_own_data()
        if save:
            self.ctx.db.save()

    def _clear_own_data(self):
        self.deleted = True
        self.data = None
        self.__dependencies = None
        self.__depends_on = None

    def _remove_self_from_dependencies(self):
        """Removes itself as a dependency from all objects in depends_on list.

        :return: [description]
        :rtype: [type]
        """
        deps = self.depends_on_metadata
        for own_dep in self.depends_on_metadata:
            doc = self.ctx.db.find_record(own_dep['record'], in_all_history=True)
            doc.dependencies_metadata = [
                dep for dep in doc.dependencies_metadata
                if dep['record'] != own_dep['own_record']
            ]
            self.ctx.db.update_record_dependencies(doc.version, doc.dependencies_metadata)

    @classmethod
    def from_flatbuffer(cls, flatbuffer):
        """For constructing ndi_document from a flatbuffer

        :param flatbuffer: [description]
        :type flatbuffer: bytes
        :return: [description]
        :rtype: Document
        """
        document = build_document.Document.GetRootAsDocument(flatbuffer, 0)
        return cls._reconstruct(document)

    @classmethod
    def _reconstruct(cls, document):
        """For constructing ndi_document from a flatbuffer object

        :param document: [description]
        :type document: build_document.Document
        :return: [description]
        :rtype: Document
        """
        return cls(
            id_=document.Id().decode(),
            data=json.loads(document.Data())
        )

    def _build(self, builder):
        """.. currentmodule:: ndi.ndi_object

        Called in NDI_Object.serialize() as part of flatbuffer bytearray generation from Session instance.

        :param builder: Builder class in flatbuffers module.
        :type builder: flatbuffers.Builder
        """

        id_ = builder.CreateString(self.id)
        data = builder.CreateString(
            json.dumps(self.data, separators=(',', ':')))

        build_document.DocumentStart(builder)
        build_document.DocumentAddId(builder, id_)
        build_document.DocumentAddData(builder, data)
        return build_document.DocumentEnd(builder)

