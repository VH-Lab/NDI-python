import abc

class Call(abc.ABC):
    """
    An abstract interface for all NDI cloud API calls.
    """

    def __init__(self):
        self.cloud_organization_id = None
        self.cloud_dataset_id = None
        self.cloud_file_id = None
        self.cloud_user_id = None
        self.cloud_document_id = None
        self.page = None
        self.page_size = None
        self.endpoint_name = None

    @abc.abstractmethod
    def execute(self):
        """
        Performs the API call.
        """
        raise NotImplementedError("This method must be implemented in a subclass.")
