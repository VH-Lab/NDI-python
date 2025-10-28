from .ido import Ido
from .documentservice import DocumentService
from .query import Query
from .document import Document
from .session import Session

class Subject(Ido, DocumentService):
    def __init__(self, local_identifier, description=''):
        super().__init__()
        self.is_valid_local_identifier_string(local_identifier)
        self.local_identifier = local_identifier
        self.description = description

    def new_document(self):
        doc = Document('subject',
            **{
                'subject.local_identifier': self.local_identifier,
                'subject.description': self.description,
                'base.id': self.id(),
                'base.name': self.local_identifier,
                'base.session_id': Session.empty_id()
            }
        )
        return doc

    def search_query(self):
        return Query('subject.local_identifier', 'exact_string', self.local_identifier, '')

    @staticmethod
    def is_valid_local_identifier_string(local_identifier):
        if not isinstance(local_identifier, str):
            raise ValueError("local_identifier must be a character string")
        if '@' not in local_identifier:
            raise ValueError("local_identifier must have an @ character.")
        if ' ' in local_identifier:
            raise ValueError("local_identifier must not have any spaces.")
        return True

    @staticmethod
    def does_subjectstring_match_session_document(session, subjectstring, makeit):
        # implementation will go here
        pass
