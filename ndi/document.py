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
        id_: T.NdiId = None,
        experiment_id: T.NdiId = None,
        document_type: str = '',
        version_depth: int = 0,
        file_id: T.NdiId = None,
        parent_id: T.NdiId = None,
        asc_path: str = '',
        dependencies: T.List[T.NdiId] = [],
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
        self.document_type = document_type
        self.version_depth = version_depth
        self.file_id = file_id
        self.parent_id = parent_id
        self.asc_path = asc_path
        self.dependencies = []
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
    def _reconstruct(cls, document: T.Document_schema) -> Document:
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
            version_depth=document.VersionDepth(),
            file_id=T.NdiId(document.FileId().decode('utf8')),
            parent_id=T.NdiId(document.ParentId().decode('utf8')),
            asc_path=document.AscPath().decode('utf8')
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
        file_id = builder.CreateString(self.file_id)
        parent_id = builder.CreateString(self.parent_id)
        asc_path = builder.CreateString(self.asc_path)

        build_document.DocumentStart(builder)
        build_document.DocumentAddId(builder, id_)
        build_document.DocumentAddExperimentId(builder, experiment_id)
        build_document.DocumentAddDocumentType(builder, document_type)
        build_document.DocumentAddVersionDepth(builder, self.version_depth)
        build_document.DocumentAddFileId(builder, file_id)
        build_document.DocumentAddParentId(builder, parent_id)
        build_document.DocumentAddAscPath(builder, asc_path)
        return build_document.DocumentEnd(builder)

    @handle_iter
    def add_dependency(self, ndi_document_id: T.NdiId) -> None:
        """Add an ndi_document object that this ndi_document depends on

        :param ndi_document: [description]
        :type ndi_document: Union[Document, List[Document]]
        :return: [description]
        :rtype: Union[None, List[None]]
        """
        self.dependencies.append(ndi_document_id)

    def set_document_extension(self, document_extension: T.DocumentExtension) -> None:
        """Sets the document_extension for this ndi_document

        :param document_extension: [description]
        :type document_extension: DocumentExtension
        """
        self.document_extension = document_extension
        self.document_extension.document_id = self.id
        self.document_type = type(document_extension).__name__

    def _save_updates(self) -> None:
        """Updates version and creates a new id for this ndi_document.

        Also updates document_extension with new ndi_document id.

        To be used in database implementations only.
        """
        self.parent_id = self.id
        super().__init__(None)
        if self.document_extension:
            self.document_extension.document_id = self.id
        self.version_depth += 1
