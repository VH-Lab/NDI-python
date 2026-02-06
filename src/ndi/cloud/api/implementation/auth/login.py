from ...call import Call
from ... import url
import requests
import json

class Login(Call):
    """
    Implementation class for user authentication.
    """

    def __init__(self, email, password):
        """
        Creates a new Login API call object.

        Args:
            email: The user's email address.
            password: The user's password.
        """
        self.email = email
        self.password = password
        self.endpoint_name = 'login'

    def execute(self):
        """
        Performs the API call to log in the user.
        """
        api_url = url.get_url(self.endpoint_name)

        payload = {
            'email': self.email,
            'password': self.password
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            return True, response.json(), response, api_url
        else:
            try:
                answer = response.json()
            except json.JSONDecodeError:
                answer = response.text
            return False, answer, response, api_url
