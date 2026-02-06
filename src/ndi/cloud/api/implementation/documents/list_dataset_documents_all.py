from ...call import Call
from .list_dataset_documents import ListDatasetDocuments

class ListDatasetDocumentsAll(Call):
    """
    Implementation class for listing all documents in a dataset.
    """

    def __init__(self, dataset_id, page_size=20):
        """
        Creates a new ListDatasetDocumentsAll API call object.

        Args:
            dataset_id (str): The ID of the dataset.
            page_size (int, optional): The number of documents per page. Defaults to 20.
        """
        self.dataset_id = dataset_id
        self.page_size = page_size
        self.endpoint_name = 'list_dataset_documents'

    def execute(self):
        """
        Performs the API call to list all documents.
        """
        all_documents = []
        page = 1
        last_response = None
        last_url = None

        while True:
            api_call = ListDatasetDocuments(self.dataset_id, page=page, page_size=self.page_size)
            success, answer, response, url = api_call.execute()

            last_response = response
            last_url = url

            if not success:
                return False, answer, response, url

            if not isinstance(answer, list):
                return False, "Unexpected response format: expected a list", response, url

            all_documents.extend(answer)

            if len(answer) < self.page_size:
                break

            page += 1

        return True, all_documents, last_response, last_url
