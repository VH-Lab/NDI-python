from ..ido import Ido as IDO
from ..time.syncgraph import SyncGraph
from ..cache import Cache

class Session:
    """
    An NDI session.
    """

    def __init__(self, reference):
        """
        Initializes a new Session object.

        Args:
            reference: A unique reference for the session.
        """
        self.reference = reference
        self.identifier = IDO().id()
        self.syncgraph = SyncGraph(self)
        self.cache = Cache()
        self.database = None  # To be implemented
        self.dataset = None

    def id(self):
        """
        Returns the unique identifier of the session.
        """
        return self.identifier

    def daqsystem_add(self, dev):
        """
        Adds a DAQ system to the session.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def daqsystem_rm(self, dev):
        """
        Removes a DAQ system from the session.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def daqsystem_load(self, **kwargs):
        """
        Loads DAQ systems from the session.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def daqsystem_clear(self):
        """
        Removes all DAQ systems from the session.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def database_add(self, document):
        """
        Adds a document to the session's database.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def database_rm(self, doc_unique_id, **kwargs):
        """
        Removes a document from the session's database.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def database_search(self, searchparameters):
        """
        Searches for documents in the session's database.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def getpath(self):
        """
        Returns the path of the session. This is an abstract method.
        """
        return None

    def getprobes(self, *args, **kwargs):
        """
        Returns all probes found in the session.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def getelements(self, *args, **kwargs):
        """
        Returns all elements found in the session.
        """
        raise NotImplementedError("This method is not yet implemented.")
