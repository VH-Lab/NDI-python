from ...call import Call
from ... import url
from .... import authenticate
import requests
import json

class VerifyUser(Call):
    """
    Implementation class for verifying a new user account.
    """

    def __init__(self, email, confirmation_code):
        """
        Creates a new VerifyUser API call object.

        Args:
            email: The user's email address.
            confirmation_code: The code sent to the user's email.
        """
        self.email = email
        self.confirmation_code = confirmation_code
        self.endpoint_name = 'verify_user'

    def execute(self):
        """
        Performs the API call to verify the user.
        """
        token = authenticate()
        api_url = url.get_url(self.endpoint_name)

        payload = {
            'email': self.email,
            'confirmationCode': self.confirmation_code
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
