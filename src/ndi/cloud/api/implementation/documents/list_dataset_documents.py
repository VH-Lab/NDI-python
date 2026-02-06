from ...call import Call
from ... import url
from ....authenticate import authenticate
import requests
import json

class ListDatasetDocuments(Call):
    """
    Implementation class for listing documents in a dataset.
    """

    def __init__(self, dataset_id, page=1, page_size=20):
        """
        Creates a new ListDatasetDocuments API call object.

        Args:
            dataset_id (str): The ID of the dataset.
            page (int, optional): The page number. Defaults to 1.
            page_size (int, optional): The number of documents per page. Defaults to 20.
        """
        self.dataset_id = dataset_id
        self.page = page
        self.page_size = page_size
        self.endpoint_name = 'list_dataset_documents'

    def execute(self):
        """
        Performs the API call to list documents.
        """
        token = authenticate()

        api_url = url.get_url(self.endpoint_name, dataset_id=self.dataset_id, page=self.page, page_size=self.page_size)

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
