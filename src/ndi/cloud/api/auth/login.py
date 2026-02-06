from ..implementation.auth.login import Login as LoginImpl

def login(email, password):
    """
    Authenticates a user and retrieves a token.

    Args:
        email: The user's email address.
        password: The user's password.

    Returns:
        A tuple of (success, answer, api_response, api_url).
    """
    api_call = LoginImpl(email, password)
    return api_call.execute()
