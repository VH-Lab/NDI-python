from ...call import Call
from ... import url
import requests
import json

class ResendConfirmation(Call):
    """
    Implementation class for resending a user confirmation email.
    """

    def __init__(self, email):
        """
        Creates a new ResendConfirmation API call object.

        Args:
            email: The email address to which the confirmation should be sent.
        """
        self.email = email
        self.endpoint_name = 'resend_confirmation'

    def execute(self):
        """
        Performs the API call to resend the confirmation email.
        """
        api_url = url.get_url(self.endpoint_name)

        payload = {
            'email': self.email
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/ '
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
