from ...call import Call
from ... import url
from .... import authenticate
import requests
import json
import os

class ListDatasets(Call):
    """
    Implementation class for listing datasets in an organization.
    """

    def __init__(self, cloud_organization_id=None):
        """
        Creates a new ListDatasets API call object.

        Args:
            cloud_organization_id: The ID of the organization. If not
                provided, the environment variable NDI_CLOUD_ORGANIZATION_ID
                will be used.
        """
        self.cloud_organization_id = cloud_organization_id
        self.endpoint_name = 'list_datasets'

    def execute(self):
        """
        Performs the API call to list datasets.
        """
        token = authenticate()

        organization_id = self.cloud_organization_id
        if organization_id is None:
            organization_id = os.getenv('NDI_CLOUD_ORGANIZATION_ID')

        if organization_id is None:
            raise ValueError("Organization ID must be provided or set as an environment variable.")

        api_url = url.get_url(self.endpoint_name, organization_id=organization_id)

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.get(api_url, headers=headers)

        if response.status_code == 200:
            return True, response.json().get('datasets', []), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
