from __future__ import annotations
import ndi.types as T
from .schema import Document as build_document
import json
from .ndi_object import NDI_Object


class Document(NDI_Object):
    """
    A flatbuffer interface for documents.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """
    def __init__(self, data: dict, type_: str = '', name: str = '', experiment_id: str = '', id_=None):
        """Creates new ndi_document

        :param id_: [description], defaults to None
        :type id_: T.NdiId, optional
        :param data: [description], defaults to None
        :type data: dict, optional
        """
        super().__init__(id_)
        self.data = {
            '_metadata': {
                'name': name,
                'type': type_,
                'experiment_id': experiment_id,
                'parent_id': '',
                'asc_path': '',
                'version_depth': 0,
                'latest_version': True,
            },
            '_dependencies': {},
            **data
        }

    @property
    def metadata(self):
        return self.data['_metadata']

    @metadata.setter
    def metadata(self, new_metadata):
        self.data['_metadata'] = new_metadata
    
    @property
    def dependencies(self):
        return self.data['_dependencies']

    @dependencies.setter
    def dependencies(self, dependencies):
        self.data['_dependencies'] = dependencies

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

        Called in NDI_Object.serialize() as part of flatbuffer bytearray generation from Experiment instance.

        :param builder: Builder class in flatbuffers module.
        :type builder: flatbuffers.Builder
        """
        self.data['_dependencies'] = {
            key: dep.id if isinstance(dep, Document) else dep 
            for key, dep in self.dependencies.items() }

        id_ = builder.CreateString(self.id)
        data = builder.CreateString(json.dumps(self.data, separators=(',', ':')))

        build_document.DocumentStart(builder)
        build_document.DocumentAddId(builder, id_)
        build_document.DocumentAddData(builder, data)
        return build_document.DocumentEnd(builder)

    def save_updates(self):
        """Updates version and creates a new id for this ndi_document and saves changes in database.

        Updates id, version_depth, parent_id with previous id, and document_extension with new ndi_document id.
        Adds parent_id to asc_path.

        To be used in database implementations only.
        """
        parent_id = self.id
        self.metadata['latest_version'] = False
        self.ctx.update(self, force=True)
        super().__init__(None)
        metadata = self.metadata
        metadata['parent_id'] = parent_id
        metadata['asc_path'] = ',' + metadata['parent_id'] + metadata['asc_path']
        metadata['version_depth'] += 1
        metadata['latest_version'] = True
        self.dependencies = {}

        if not self.ctx:
            """Will fire if the document is not in the database (ctx is attached any time a document is added or retrieved from the database; only user-initialized Documents should not have a ctx)."""
            # TODO: make this error message more helpful when ctx is well defined
            raise RuntimeError('This document is not attached to a database.')
        else:
            self.ctx.add(self)

    def get_history(self):
        """oldest to newest"""
        ids = self.metadata['asc_path'].split(',')[1:]
        return [self.ctx.find_by_id(id) for id in reversed(ids)]

    def __check_dependency_key_exists(self, key: str):
        dependencies = self.dependencies
        return any([key is extant for extant in dependencies.keys()])

    def __check_dependency_id_exists(self, id_: str):
        return any([id_ is extant_id for extant_id in self.dependencies.values()])

    def add_dependency(self, ndi_document: T.Document, key: str = None):
        key = key or ndi_document.metadata['name']
        if self.__check_dependency_key_exists(key):
            raise RuntimeError('Dependency key is already in use (dependency keys default to the document name if not specified).')
        elif self.__check_dependency_id_exists(ndi_document.id):
            dependency_name = ndi_document.metadata['name']
            own_name = self.metadata['name']
            raise RuntimeError(f'Document {dependency_name} is already a dependency of document {own_name}.')
        else:
            new_dependency = {key: ndi_document.id}
            self.dependencies = { 
                **self.dependencies, 
                **new_dependency 
            }
            self.ctx.add(ndi_document)
            self.ctx.update(self, force=True)

    def get_dependencies(self):
        for key, value in self.dependencies.items():
            if isinstance(value, str):
                self.dependencies[key] = self.ctx.find_by_id(value)
        return self.dependencies

    def delete(self, force=False, remove_history=False,):
        if force:
            deletees = list(self.get_dependencies().values())
            if remove_history:
                deletees.extend(self.get_history())
            for ndi_document in deletees:
                ndi_document.delete(force=force, remove_history=remove_history)
            self.ctx.delete(self)
        else:
            raise RuntimeWarning('Are you sure you want to delete this document? This will permanently remove it and its dependencies. To delete anyway, use the force argument: db.update(document, force=True). To clear the version history of this document and related dependencies, use the remove_history argument.')