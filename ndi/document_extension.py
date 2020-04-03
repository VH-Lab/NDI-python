from .ndi_object import NDI_Object
from abc import ABC, abstractmethod


class DocumentExtension(NDI_Object, ABC):
    """
    Abstract class for implementing user-defined flatbuffer schema.

    Subclass implementations are used to create custom ndi_documents
    """
    @abstractmethod
    def __init__(self, document_id=''):
        self.document_id = document_id

    @classmethod
    @abstractmethod
    def from_flatbuffer(cls):
        pass

    @classmethod
    @abstractmethod
    def _reconstruct(cls):
        pass

    @abstractmethod
    def _build(self):
        pass
