import abc

class Database(abc.ABC):
    """
    An abstract database class for NDI.
    """

    def __init__(self, path, session_unique_reference):
        """
        Initializes a new Database object.
        """
        self.path = path
        self.session_unique_reference = session_unique_reference

    @abc.abstractmethod
    def add(self, doc, **kwargs):
        raise NotImplementedError

    @abc.abstractmethod
    def read(self, doc_id):
        raise NotImplementedError

    @abc.abstractmethod
    def remove(self, doc_id):
        raise NotImplementedError

    @abc.abstractmethod
    def search(self, search_parameters):
        raise NotImplementedError

    @abc.abstractmethod
    def alldocids(self):
        raise NotImplementedError

    def clear(self, areyousure='no'):
        """
        Removes all documents from the database.
        """
        if areyousure.lower() == 'yes':
            ids = self.alldocids()
            for doc_id in ids:
                self.remove(doc_id)
        else:
            print("Not clearing database.")
