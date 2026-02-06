import os
import getpass
from .internal import token_utils
from .api.auth import login as auth_login

def authenticate(username=None, interaction_enabled=True):
    """
    Authenticates using secret, environment variables or prompt.

    Args:
        username (str, optional): Username to use for login.
        interaction_enabled (bool, optional): Whether interactive steps are enabled.

    Returns:
        str: The authentication token.
    """

    # Check if already authenticated
    if is_authenticated(username):
        token, _ = token_utils.get_active_token()
        return token

    # Check environment variables
    if authenticated_with_environment_variable(username):
         token, _ = token_utils.get_active_token()
         return token

    # Prompt user
    if interaction_enabled:
        if prompt_login(username):
             token, _ = token_utils.get_active_token()
             return token

    # If we get here, authentication failed or was skipped
    # Matlab doesn't return anything or returns existing token (which might be empty/invalid?)
    # But here we want to return a valid token or raise error?
    # Matlab returns token found at the end.

    token, _ = token_utils.get_active_token()
    if not token:
        # If no token, maybe we should raise an error if interaction was enabled but failed?
        # Or just return None/empty string?
        # Matlab doesn't explicitly raise error in the main function, but prompt might.
        pass

    return token

def is_authenticated(username=None):
    token, _ = token_utils.get_active_token()
    if not token:
        return False

    if username:
        decoded_token = token_utils.decode_jwt(token)
        if decoded_token.get('email') != username:
            return False

    return True

def authenticated_with_environment_variable(requested_username=None):
    username = os.environ.get("NDI_CLOUD_USERNAME")
    password = os.environ.get("NDI_CLOUD_PASSWORD")

    if username and password:
        if requested_username and username != requested_username:
            return False
        return perform_login(username, password)
    return False

def prompt_login(username=None):
    if not username:
        username = input("Enter NDI Cloud Email: ")

    password = getpass.getpass(f"Enter Password for {username}: ")

    return perform_login(username, password)

def perform_login(username, password):
    success, answer, response, _ = auth_login.login(username, password)

    if success:
        token = answer.get('token')
        # Handle organizations. Structure might be user -> organizations -> id?
        # Matlab: answer.user.organizations.id
        # We need to be careful about structure.
        # Let's try to find it.
        user = answer.get('user', {})
        organizations = user.get('organizations', [])
        organization_id = ''

        # If organizations is a list, take first? Or checks for specific one?
        # Matlab code: answer.user.organizations.id. This suggests organizations is a struct (dict), not a list?
        # Or maybe it is a list of structs and Matlab auto-vectorizes?
        # But commonly in these APIs it's a list.
        # If it's a list, we might pick the first one.

        if isinstance(organizations, list) and len(organizations) > 0:
             organization_id = organizations[0].get('id')
        elif isinstance(organizations, dict):
             organization_id = organizations.get('id')

        os.environ['NDI_CLOUD_TOKEN'] = token
        if organization_id:
            os.environ['NDI_CLOUD_ORGANIZATION_ID'] = organization_id

        return True
    else:
        print(f"Authentication failed: {response.status_code} {response.reason}")
        # print body?
        return False
