from ...call import Call
from ... import url
from ....authenticate import authenticate
import requests
import json

class GetBulkDownloadURL(Call):
    """
    Implementation class for getting a bulk download URL.
    """

    def __init__(self, dataset_id, document_ids=None):
        """
        Creates a new GetBulkDownloadURL API call object.

        Args:
            dataset_id (str): The ID of the dataset.
            document_ids (list of str, optional): List of cloud document IDs to download.
                                                  If None or empty, all documents are included.
        """
        self.dataset_id = dataset_id
        self.document_ids = document_ids if document_ids is not None else []
        self.endpoint_name = 'bulk_download_documents'

    def execute(self):
        """
        Performs the API call.
        """
        token = authenticate()
        api_url = url.get_url(self.endpoint_name, dataset_id=self.dataset_id)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        # The body specifies which document IDs to include
        data = {'documentIds': self.document_ids}

        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code in [200, 201]:
            try:
                answer = response.json().get('url')
                return True, answer, response, api_url
            except json.JSONDecodeError:
                return False, response.text, response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
