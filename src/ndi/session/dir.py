from . import Session

class Dir(Session):
    """
    An NDI session associated with a directory.
    """

    def __init__(self, reference, path_name=None):
        """
        Initializes a new Dir session.

        Args:
            reference: The reference for the session or the path if path_name is None.
            path_name: The path to the session directory.
        """
        if path_name is None:
            path_name = reference

        super().__init__(reference)
        self.path = path_name
        # In a full implementation, we would initialize the database here.
        # self.database = SomeDatabaseClass(self.path)

    def getpath(self):
        """
        Returns the path of the session.
        """
        return self.path
