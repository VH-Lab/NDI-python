from ...call import Call
from ... import url
from ....authenticate import authenticate
import requests
import json

class DeleteDocument(Call):
    """
    Implementation class for deleting a document from a dataset.
    """

    def __init__(self, dataset_id, document_id):
        """
        Creates a new DeleteDocument API call object.

        Args:
            dataset_id (str): The ID of the dataset.
            document_id (str): The ID of the document.
        """
        self.dataset_id = dataset_id
        self.document_id = document_id
        self.endpoint_name = 'delete_document'

    def execute(self):
        """
        Performs the API call to delete a document.
        """
        token = authenticate()

        api_url = url.get_url(self.endpoint_name, dataset_id=self.dataset_id, document_id=self.document_id)

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.delete(api_url, headers=headers)

        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
