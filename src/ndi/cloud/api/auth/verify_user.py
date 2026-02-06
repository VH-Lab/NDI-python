from ..implementation.auth.verify_user import VerifyUser as VerifyUserImpl

def verify_user(email, confirmation_code):
    """
    Verifies a user account with a confirmation code.

    Args:
        email: The user's email address.
        confirmation_code: The confirmation code from the email.

    Returns:
        A tuple of (success, answer, api_response, api_url).
    """
    api_call = VerifyUserImpl(email, confirmation_code)
    return api_call.execute()
