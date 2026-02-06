from ...call import Call
from ... import url
from ....authenticate import authenticate
import requests
import json

class GetDataset(Call):
    """
    Implementation class for getting dataset details.
    """

    def __init__(self, dataset_id):
        """
        Creates a new GetDataset API call object.

        Args:
            dataset_id (str): The ID of the dataset.
        """
        self.dataset_id = dataset_id
        self.endpoint_name = 'get_dataset'

    def execute(self):
        """
        Performs the API call.
        """
        token = authenticate()
        api_url = url.get_url(self.endpoint_name, dataset_id=self.dataset_id)

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
