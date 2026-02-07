from ...call import Call
from ... import url
from ....authenticate import authenticate
import requests
import json

class GetFileUploadURL(Call):
    """
    Implementation class for getting a file upload URL.
    """

    def __init__(self, dataset_id, file_uid, organization_id=None):
        """
        Creates a new GetFileUploadURL API call object.

        Args:
            dataset_id (str): The ID of the dataset.
            file_uid (str): The UID of the file.
            organization_id (str, optional): The ID of the organization. If not provided, it will be retrieved from the environment.
        """
        self.dataset_id = dataset_id
        self.file_uid = file_uid
        self.organization_id = organization_id
        self.endpoint_name = 'get_file_upload_url'

    def execute(self):
        """
        Performs the API call.
        """
        token = authenticate()

        # Pass organization_id if available, otherwise url.get_url will try env var
        kwargs = {
            'dataset_id': self.dataset_id,
            'file_uid': self.file_uid
        }
        if self.organization_id:
            kwargs['organization_id'] = self.organization_id

        try:
            api_url = url.get_url(self.endpoint_name, **kwargs)
        except ValueError as e:
            # Likely missing organizationId
            return False, str(e), None, None

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
