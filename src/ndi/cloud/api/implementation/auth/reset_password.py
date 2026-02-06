from ...call import Call
from ... import url
from .... import authenticate
import requests
import json

class ResetPassword(Call):
    """
    Implementation class for requesting a password reset email.
    """

    def __init__(self, email):
        """
        Creates a new ResetPassword API call object.

        Args:
            email: The email address for the password reset request.
        """
        self.email = email
        self.endpoint_name = 'reset_password'

    def execute(self):
        """
        Performs the API call to request a password reset email.
        """
        token = authenticate()
        api_url = url.get_url(self.endpoint_name)

        payload = {
            'email': self.email
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        if response.status_code in [200, 201]:
            return True, response.json(), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
