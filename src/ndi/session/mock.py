import os
import shutil
import tempfile
from .dir import Dir

class Mock(Dir):
    """
    A mock NDI session for testing.
    """

    def __init__(self):
        """
        Initializes a new Mock session.
        """
        ref = 'mock_test'
        dirname = os.path.join(tempfile.gettempdir(), 'mock_test')

        if os.path.exists(dirname):
            shutil.rmtree(dirname)
        os.makedirs(dirname)

        super().__init__(ref, dirname)

        # In a full implementation, we would also copy mock data files,
        # create a mock DAQ device, and add a mock subject to the database.
        self._setup_mock_data()

    def _setup_mock_data(self):
        """
        Sets up mock data for the session.
        """
        # This is a placeholder for the data setup logic.
        # In the future, this method will:
        # 1. Copy necessary data files to the temp directory.
        # 2. Create and add a mock DAQ system.
        # 3. Create and add a mock subject to the database.
        pass
