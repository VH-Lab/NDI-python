from __future__ import annotations
import ndi.types as T
from .schema import Document as build_document
import json
from .flatbuffer_object import Flatbuffer_Object
from .context import Context
from did.time import current_time
from did import Query as Q
from did.versioning import hash_document
from contextlib import contextmanager
from .exceptions import InvalidDocument, DocumentIdentityError

class BinaryWrapper:
    def __init__(self, binary_collection: T.BinaryCollection = None, document: Document = None):
        self.document = document
        self.binary_collection = binary_collection
    
    def connect(self, binary_collection: T.BinaryCollection = None):
        self.binary_collection = binary_collection

    def open_write_stream(self, name):
        return self.binary_collection.open_write_stream(self.document, name)

    def open_read_stream(self, name, record=None):
        return self.binary_collection.open_read_stream(self.document, name, record)



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
        self.binary = BinaryWrapper(document=self)
        if data:
            self.data = data
            try:
                if data['base']['id']:
                    self.id = data['base']['id']
                else:
                    data['base']['id'] = self.id
            except KeyError:
                pass # Handle error in self.validate
            self.validate(data) # throws InvalidDocument if invalid
        else:   
            self.data = {
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
                    'definition': '',
                    'validation': '',
                    'name': '',
                    'property_list_name': '',
                    'class_version': '',
                    'superclasses': [],
                },
            }
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
    def binary_files(self):
        return self.data['binary_files']

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
            self.ctx.did.save()

    def update(self, save=None):
        """
        Stages document data update.
        """
        with self.available_ctx():
            self.ctx.did.update(self, save=save)
            self.__dependencies = None

    def upsert(self, save=None):
        """
        Stages document data upsert.
        """
        with self.available_ctx():
            self.ctx.did.upsert(self, save=save)
            self.__dependencies = None

    def refresh(self, snapshot=None, commit=None):
        self_in_db = self.ctx.did.find_by_id(self.id, snapshot, commit)
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

    def checkout(self, record):
        doc = self.ctx.did.find_record(record, in_all_history=True)
        if doc.id == self.id:
            self.data = doc.data
        else:
            raise DocumentIdentityError(f'The given record (id = {doc.id}) is not this document.')
        return self

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
            'own_snapshot': self.snapshot,
            'dependency_snapshot': related_document.snapshot
        }

    def add_dependency(self, ndi_document: T.Document, name: str = None, save=None):
        name = name or ndi_document.data['base']['name'] or ndi_document.id
        self.__verify_dependency(ndi_document, name)
        self.ctx.did.add(ndi_document, save=False)
        ndi_document.with_ctx(self.ctx)
        self.__link_dependency(ndi_document, name)
        self.ctx.did.update(self, save=False)
        if save:
            self.ctx.did.save()
    
    def link_dependency(self, ndi_document: T.Document, name: str = None, save=None):
        name = name or ndi_document.data['base']['name'] or ndi_document.id
        self.__verify_dependency(ndi_document, name)
        self.ctx.did.update(ndi_document, save=False)
        ndi_document.with_ctx(self.ctx)
        self.__link_dependency(ndi_document, name)
        self.ctx.did.update(self, save=False)
        if save:
            self.ctx.did.save()

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

    def get_dependencies(self, scope='current'):
        dependencies = {}
        if scope == 'existing':
            for dependency in self.dependencies_metadata:
                dependencies[dependency['name']] = self.ctx.did.find_by_id(dependency['id'])
        elif scope == 'all':
            for dependency in self.dependencies_metadata:
                dependencies[dependency['name']] = self.ctx.did.find_by_id(
                    dependency['id'], snapshot=dependency['dependency_snapshot']
                )
        elif scope == 'current':
            relevant_deps = [dep for dep in self.dependencies_metadata if dep['own_snapshot'] ==  self.snapshot]
            for dependency in relevant_deps:
                dependencies[dependency['name']] = self.ctx.did.find_by_id(
                    dependency['id'], snapshot=dependency['dependency_snapshot']
                )

        return dependencies

    def get_depends_on(self):
        depends_on = {}
        relevant_deps = [dep for dep in self.depends_on_metadata if dep['own_snapshot'] ==  self.snapshot]
        for dep in relevant_deps:
            depends_on[dep['name']] = self.ctx.did.find_by_id(
                dep['id'], snapshot=dep['dependency_snapshot']
            )
        return depends_on


    def delete(self, save=None):
        deletees = self.get_dependencies()
        for ndi_document in deletees.values():
            ndi_document.delete(save=False)
        self._remove_self_from_dependencies()
        self.ctx.did.delete(self, save=False)
        self._clear_own_data()
        if save:
            self.ctx.did.save()

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
        for own_dep in self.depends_on_metadata:
            doc = self.ctx.did.find_by_id(own_dep['id'], snapshot=own_dep['dependency_snapshot'])
            doc.dependencies_metadata = [
                dep for dep in doc.dependencies_metadata
                if dep['id'] != self.id
            ]
            self.ctx.did.update_record_dependencies(doc.version, doc.dependencies_metadata)

    def validate(self, data=None):
        data = data or self.data
        expected_fields = {
            'depends_on': list,
            'dependencies': list,
            'binary_files': list,
            'base': {
                'id': str,
                'session_id': str,
                'name': str,
                'datestamp': str,
                'snapshots': list,
                'records': list,
            },
            'document_class': {
                'definition': str,
                'validation': str,
                'name': str,
                'property_list_name': str,
                'class_version': str,
                'superclasses': list,
            }
        }
        def check_fields(dict_, reference, path=['data']):
            errors = []
            for key, value in reference.items():
                key_exists = False
                try:
                    dict_[key]
                    key_exists = True
                except KeyError:
                    errors.append(f'{".".join(path)} is missing key "{key}".')
                if key_exists:
                    path_w_key = [*path, key]
                    if type(value) is dict:
                        errors = [
                            *errors,
                            *check_fields(dict_[key], value, path_w_key)
                        ]
                    elif type(dict_[key]) is not value:
                        errors.append(f'Value of {".".join(path_w_key)} must be of {value}.')
            return errors
        errors = check_fields(data, expected_fields)
        if errors:
            nl = '\n  '
            raise InvalidDocument(f'The given data contains the following errors:{nl}{nl.join(errors)}')

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

