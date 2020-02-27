from __future__ import annotations
from .ndi_object import NDI_Object
from .decorators import typechecked_class, handle_iter
import ndi.schema.Document as build_document
import ndi.types as T


@typechecked_class
class Document(NDI_Object):
    """
    A flatbuffer interface for documents.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    def __init__(
        self,
        document_extension: T.Optional[T.DocumentExtension] = None,
        experiment_id: T.NdiId = None,
        dependencies: T.List[T.NdiId] = [],
        version: int = 1,
        id_: T.NdiId = None,
        document_type: str = '',
        base_id: T.NdiId = None
    ) -> None:
        """Creates new ndi_document

        :param document_extension: [description], defaults to None
        :type document_extension: DocumentExtension, optional
        :param experiment_id: [description], defaults to ''
        :type experiment_id: str, optional
        :param dependencies: [description], defaults to []
        :type dependencies: List[Document], optional
        :param version: [description], defaults to 1
        :type version: int, optional
        :param id_: [description], defaults to ''
        :type id_: str, optional
        :param document_type: [description], defaults to ''
        :type document_type: str, optional
        :param base_id: [description], defaults to ''
        :type base_id: str, optional
        """
        super().__init__(id_)
        self.experiment_id = experiment_id
        self.version = version
        self.base_id = base_id if version > 1 else self.id
        self.dependencies: T.List[T.NdiId] = []
        self.add_dependency(dependencies)
        if document_extension:
            self.set_document_extension(document_extension)

    @classmethod
    def from_flatbuffer(cls, flatbuffer: bytes) -> Document:
        """For constructing ndi_document from a flatbuffer

        :param flatbuffer: [description]
        :type flatbuffer: bytes
        :return: [description]
        :rtype: Document
        """
        document = build_document.Document.GetRootAsDocument(flatbuffer, 0)
        return cls._reconstruct(document)

    @classmethod
    def _reconstruct(cls, document: build_document.Document) -> Document:
        """For constructing ndi_document from a flatbuffer object

        :param document: [description]
        :type document: build_document.Document
        :return: [description]
        :rtype: Document
        """
        return cls(
            id_=T.NdiId(document.Id().decode('utf8')),
            experiment_id=T.NdiId(document.ExperimentId().decode('utf8')),
            document_type=document.DocumentType().decode('utf8'),
            base_id=T.NdiId(document.BaseId().decode('utf8')),
            version=document.Version()
        )

    def _build(self, builder: T.Builder) -> T.BuildOffset:
        """.. currentmodule:: ndi.ndi_object

        Called in NDI_Object.serialize() as part of flatbuffer bytearray generation from Experiment instance.

        :param builder: Builder class in flatbuffers module.
        :type builder: flatbuffers.Builder
        """
        id_ = builder.CreateString(self.id)
        experiment_id = builder.CreateString(self.experiment_id)
        document_type = builder.CreateString(self.document_type)
        base_id = builder.CreateString(self.base_id)

        build_document.DocumentStart(builder)
        build_document.DocumentAddId(builder, id_)
        build_document.DocumentAddExperimentId(builder, experiment_id)
        build_document.DocumentAddDocumentType(builder, document_type)
        build_document.DocumentAddBaseId(builder, base_id)
        build_document.DocumentAddVersion(builder, self.version)
        return build_document.DocumentEnd(builder)

    @handle_iter
    def add_dependency(self, ndi_document: T.NdiId) -> None:
        """Add an ndi_document object that this ndi_document depends on

        :param ndi_document: [description]
        :type ndi_document: Union[Document, List[Document]]
        :return: [description]
        :rtype: Union[None, List[None]]
        """
        self.dependencies.append(ndi_document)

    def set_document_extension(self, document_extension: T.DocumentExtension) -> None:
        """Sets the document_extension for this ndi_document

        :param document_extension: [description]
        :type document_extension: DocumentExtension
        """
        self.document_extension = document_extension
        if self.document_extension:
            self.document_extension.document_id = self.id
            self.document_type = type(document_extension).__name__

    def _save_updates(self) -> None:
        """Updates version and creates a new id for this ndi_document.

        Also updates document_extension with new ndi_document id.

        To be used in database implementations only.
        """
        super().__init__(None)
        if self.document_extension:
            self.document_extension.document_id = self.id
        self.version += 1
