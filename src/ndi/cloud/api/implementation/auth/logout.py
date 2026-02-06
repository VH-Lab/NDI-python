from ...call import Call
from ... import url
from .... import authenticate
import requests
import json

class Logout(Call):
    """
    Implementation class for user logout.
    """

    def __init__(self):
        """
        Creates a new Logout API call object.
        """
        self.endpoint_name = 'logout'

    def execute(self):
        """
        Performs the API call to log out the user.
        """
        token = authenticate()
        api_url = url.get_url(self.endpoint_name)

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.post(api_url, headers=headers)

        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
