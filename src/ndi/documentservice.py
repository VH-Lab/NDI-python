from .document import Document

class DocumentService:
    def new_document(self, document_type='base', **kwargs):
        return Document(document_type, **kwargs)

    def search_query(self):
        raise NotImplementedError
