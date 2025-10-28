from ..implementation.auth.logout import Logout as LogoutImpl

def logout():
    """
    Logs out the current user and invalidates their token.

    Returns:
        A tuple of (success, answer, api_response, api_url).
    """
    api_call = LogoutImpl()
    return api_call.execute()
