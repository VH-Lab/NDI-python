from ..session import Session

class Dataset:
    """
    An NDI dataset, which is a collection of NDI sessions.
    """

    def __init__(self, reference):
        """
        Initializes a new Dataset object.

        Args:
            reference: A unique reference for the dataset.
        """
        self._session = Session(reference)  # The dataset's own session
        self._session.dataset = self
        self._session_info = []
        self._session_array = []

    def id(self):
        """
        Returns the unique identifier of the dataset.
        """
        return self._session.id()

    def reference(self):
        """
        Returns the reference string for the dataset.
        """
        return self._session.reference

    def add_linked_session(self, session_obj):
        """
        Links an NDI session to the dataset.

        This is a simplified implementation. The full implementation will
        require database and document handling.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def add_ingested_session(self, session_obj):
        """
        Ingests an NDI session into the dataset.

        This is a simplified implementation. The full implementation will
        require database and document handling.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def open_session(self, session_id):
        """
        Opens an NDI session from the dataset.

        This is a simplified implementation.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def session_list(self):
        """
        Returns a list of sessions in the dataset.

        This is a simplified implementation.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def getpath(self):
        """
        Returns the path of the dataset.
        """
        return self._session.getpath()

    def database_add(self, document):
        """
        Adds a document to the dataset.

        This is a simplified implementation.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def database_rm(self, doc_unique_id, **options):
        """
        Removes a document from the dataset.

        This is a simplified implementation.
        """
        raise NotImplementedError("This method is not yet implemented.")

    def database_search(self, searchparameters):
        """
        Searches for a document in the dataset.

        This is a simplified implementation.
        """
        raise NotImplementedError("This method is not yet implemented.")
