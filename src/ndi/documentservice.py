from .document import Document
import abc

class DocumentService(abc.ABC):
    def new_document(self, document_type='base', **kwargs):
        return Document(document_type, **kwargs)

    @abc.abstractmethod
    def search_query(self):
        raise NotImplementedError
