from ...call import Call
from ... import url
from ....authenticate import authenticate
import requests
import json
import os

class CreateDataset(Call):
    """
    Implementation class for creating a new dataset.
    """

    def __init__(self, dataset_info, organization_id=None):
        """
        Creates a new CreateDataset API call object.

        Args:
            dataset_info (dict): The dataset information to create.
            organization_id (str, optional): The ID of the organization.
        """
        self.dataset_info = dataset_info
        self.organization_id = organization_id
        self.endpoint_name = 'create_dataset'

    def execute(self):
        """
        Performs the API call to create a dataset.
        """
        token = authenticate()

        organization_id = self.organization_id
        if organization_id is None:
            organization_id = os.getenv('NDI_CLOUD_ORGANIZATION_ID')

        if organization_id is None:
            raise ValueError("Organization ID must be provided or set as an environment variable.")

        api_url = url.get_url(self.endpoint_name, organization_id=organization_id)

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.post(api_url, headers=headers, json=self.dataset_info)

        if response.status_code in [200, 201]:
            return True, response.json(), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
