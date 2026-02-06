import os
from .api.auth import logout as auth_logout

def logout():
    """
    Logs out the current user, clears environment variables and invalidates the token.
    """
    # Call API to invalidate token
    try:
        auth_logout.logout()
    except Exception as e:
        print(f"Warning: Failed to call logout API: {e}")

    # Clear environment variables
    if 'NDI_CLOUD_TOKEN' in os.environ:
        del os.environ['NDI_CLOUD_TOKEN']
    if 'NDI_CLOUD_ORGANIZATION_ID' in os.environ:
        del os.environ['NDI_CLOUD_ORGANIZATION_ID']
    if 'NDI_CLOUD_USERNAME' in os.environ:
        del os.environ['NDI_CLOUD_USERNAME']
    if 'NDI_CLOUD_PASSWORD' in os.environ:
        del os.environ['NDI_CLOUD_PASSWORD']

    print("Logged out successfully.")
