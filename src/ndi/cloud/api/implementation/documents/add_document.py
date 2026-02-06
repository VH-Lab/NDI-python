from ...call import Call
from ... import url
from ....authenticate import authenticate
import requests
import json

class AddDocument(Call):
    """
    Implementation class for adding a new document to a dataset.
    """

    def __init__(self, dataset_id, document_info):
        """
        Creates a new AddDocument API call object.

        Args:
            dataset_id (str): The ID of the dataset.
            document_info (dict): The document information to add.
        """
        self.dataset_id = dataset_id
        self.document_info = document_info
        self.endpoint_name = 'add_document'

    def execute(self):
        """
        Performs the API call to add a document.
        """
        token = authenticate()

        api_url = url.get_url(self.endpoint_name, dataset_id=self.dataset_id)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.post(api_url, headers=headers, json=self.document_info)

        if response.status_code in [200, 201]:
            return True, response.json(), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
