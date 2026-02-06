from ...call import Call
from ... import url
from .... import authenticate
import requests
import json

class GetUnpublished(Call):
    """
    Implementation class for getting unpublished datasets from NDI Cloud.
    """

    def __init__(self, page=1, page_size=20):
        """
        Creates a new GetUnpublished API call object.

        Args:
            page: The page number of results to retrieve.
            page_size: The number of results per page.
        """
        self.page = page
        self.page_size = page_size
        self.endpoint_name = 'get_unpublished'

    def execute(self):
        """
        Performs the API call to get unpublished datasets.
        """
        token = authenticate()
        api_url = url.get_url(self.endpoint_name, page=self.page, page_size=self.page_size)

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
