from ...call import Call
from ... import url
from .... import authenticate
import requests
import json

class ChangePassword(Call):
    """
    Implementation class for changing a user's password.
    """

    def __init__(self, old_password, new_password):
        """
        Creates a new ChangePassword API call object.

        Args:
            old_password: The user's current password.
            new_password: The user's desired new password.
        """
        self.old_password = old_password
        self.new_password = new_password
        self.endpoint_name = 'change_password'

    def execute(self):
        """
        Performs the API call to change the password.
        """
        token = authenticate()
        api_url = url.get_url(self.endpoint_name)

        payload = {
            'oldPassword': self.old_password,
            'newPassword': self.new_password
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
