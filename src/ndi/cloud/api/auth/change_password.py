from ..implementation.auth.change_password import ChangePassword as ChangePasswordImpl

def change_password(old_password, new_password):
    """
    Changes the current user's password.

    Args:
        old_password: The user's current password.
        new_password: The user's desired new password.

    Returns:
        A tuple of (success, answer, api_response, api_url).
    """
    api_call = ChangePasswordImpl(old_password, new_password)
    return api_call.execute()
