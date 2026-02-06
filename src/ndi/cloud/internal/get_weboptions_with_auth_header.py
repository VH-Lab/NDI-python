def get_weboptions_with_auth_header(token=None):
    """
    Returns the web options (headers) with the authentication header.

    Args:
        token (str, optional): The authentication token. If not provided, it will be retrieved using authenticate().

    Returns:
        dict: A dictionary containing the headers.
    """
    if token is None:
        from ..authenticate import authenticate
        token = authenticate()

    if not token:
        # Should we raise error?
        # Matlab might return empty or error.
        # For now, return empty headers or raise error?
        # authenticate() prints error if interactive login fails.
        pass

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    return headers
