from ..implementation.auth.resend_confirmation import ResendConfirmation as ResendConfirmationImpl

def resend_confirmation(email):
    """
    Resends a user confirmation email.

    Args:
        email: The email address to which the confirmation should be sent.

    Returns:
        A tuple of (success, answer, api_response, api_url).
    """
    api_call = ResendConfirmationImpl(email)
    return api_call.execute()
