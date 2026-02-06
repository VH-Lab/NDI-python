from ..implementation.auth.reset_password import ResetPassword as ResetPasswordImpl

def reset_password(email):
    """
    Sends a password reset email to the specified address.

    Args:
        email: The email address of the user requesting the reset.

    Returns:
        A tuple of (success, answer, api_response, api_url).
    """
    api_call = ResetPasswordImpl(email)
    return api_call.execute()
