from ...call import Call
from ... import url
from ....authenticate import authenticate
import requests
import json

class UpdateDocument(Call):
    """
    Implementation class for updating a document in a dataset.
    """

    def __init__(self, dataset_id, document_id, document_info):
        """
        Creates a new UpdateDocument API call object.

        Args:
            dataset_id (str): The ID of the dataset.
            document_id (str): The ID of the document.
            document_info (dict): The updated document information.
        """
        self.dataset_id = dataset_id
        self.document_id = document_id
        self.document_info = document_info
        self.endpoint_name = 'update_document'

    def execute(self):
        """
        Performs the API call to update a document.
        """
        token = authenticate()

        api_url = url.get_url(self.endpoint_name, dataset_id=self.dataset_id, document_id=self.document_id)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.put(api_url, headers=headers, json=self.document_info)

        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
