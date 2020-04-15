from .schema import Document as build_document
import json
from .ndi_object import NDI_Object


class Document(NDI_Object):
    """
    A flatbuffer interface for documents.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """
    def __init__(self, data, id_=None):
        """Creates new ndi_document

        :param id_: [description], defaults to None
        :type id_: T.NdiId, optional
        :param data: [description], defaults to None
        :type data: dict, optional
        """
        super().__init__(id_)
        self.data = {
            '_metadata': {
                'experiment_id': '',
                'version_depth': 0,
                'parent_id': '',
                'asc_path': '',
            },
            '_dependencies': {},
            **data
        }

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
        id_ = builder.CreateString(self.id)
        data = builder.CreateString(json.dumps(self.data, separators=(',', ':')))

        build_document.DocumentStart(builder)
        build_document.DocumentAddId(builder, id_)
        build_document.DocumentAddData(builder, data)
        return build_document.DocumentEnd(builder)

    def _save_updates(self):
        """Updates version and creates a new id for this ndi_document.

        Updates id, version_depth, parent_id with previous id, and document_extension with new ndi_document id.
        Adds parent_id to asc_path.

        To be used in database implementations only.
        """
        super().__init__(None)
        metadata = self.data['_metadata']
        metadata['parent_id'] = self.id
        metadata['asc_path'] = ',' + metadata['parent_id'] + metadata['asc_path']
        metadata['version_depth'] += 1

    def add_dependency(self, dependency):
        self.data['_dependencies'] = { **self.data['_dependencies'], **dependency }
