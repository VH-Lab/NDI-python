from .. import authenticate

def get_headers_with_auth_header():
    """
    Create a dictionary with the Authorization header.

    Returns:
        dict: Headers with 'Authorization'.
    """
    token = authenticate.authenticate()
    return {"Authorization": f"Bearer {token}"}
