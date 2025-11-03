from ..ido import Ido as IDO
from ..documentservice import DocumentService
import abc

class SyncRule(IDO, DocumentService, abc.ABC):
    """
    An abstract class for managing synchronization rules.
    """

    def __init__(self, parameters=None):
        """
        Initializes a new SyncRule object.
        """
        super().__init__()
        self.parameters = parameters if parameters is not None else {}

    def setparameters(self, parameters):
        """
        Sets the parameters for the sync rule.
        """
        is_valid, msg = self.isvalidparameters(parameters)
        if is_valid:
            self.parameters = parameters
        else:
            raise ValueError(f"Could not set parameters: {msg}")

    def isvalidparameters(self, parameters):
        """
        Checks if the given parameters are valid.
        """
        return True, ""

    @abc.abstractmethod
    def apply(self, epochnode_a, epochnode_b):
        """
        Applies the sync rule to two epoch nodes.
        """
        raise NotImplementedError
