import os
import base64
import json
import time
from datetime import datetime, timezone

def decode_jwt(token):
    """
    Decodes a JSON Web Token (JWT) and returns its payload.

    Args:
        token (str): The JWT to decode.

    Returns:
        dict: The decoded payload.
    """
    if not token:
        return {}

    parts = token.split('.')
    if len(parts) < 2:
        return {} # Invalid token format

    payload_base64 = parts[1]
    # Base64Url decoding
    payload_base64 = payload_base64.replace('-', '+').replace('_', '/')
    padding = len(payload_base64) % 4
    if padding > 0:
        payload_base64 += '=' * (4 - padding)

    try:
        payload_bytes = base64.b64decode(payload_base64)
        payload_json = payload_bytes.decode('utf-8')
        return json.loads(payload_json)
    except Exception as e:
        # In case of error (e.g. invalid base64), return empty
        return {}

def get_token_expiration(token):
    """
    Returns the expiration time of a JWT.

    Args:
        token (str): The JWT.

    Returns:
        datetime: The expiration time (UTC).
    """
    payload = decode_jwt(token)
    if 'exp' in payload:
        return datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
    return None

def get_active_token():
    """
    Retrieves the active NDI cloud token and organization ID.

    Returns:
        tuple: (token, organization_id). Token is None if expired or not found.
    """
    token = os.environ.get('NDI_CLOUD_TOKEN')
    organization_id = os.environ.get('NDI_CLOUD_ORGANIZATION_ID')

    if token:
        expiration_time = get_token_expiration(token)
        if expiration_time:
            now = datetime.now(timezone.utc)
            if now > expiration_time:
                token = None
        else:
             # If no expiration found, assume valid? Or invalid?
             # Matlab: if ~isempty(token), expiration_time = ...; if now > exp, token = ''.
             # If exp is missing, it probably won't expire? Or invalid?
             # Let's assume valid if parsing fails or no exp, unless it was invalid format.
             pass

    return token, organization_id
