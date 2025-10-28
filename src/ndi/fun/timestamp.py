from datetime import datetime, timezone

def timestamp():
    """
    Returns a current time stamp string.
    """
    now = datetime.now(timezone.utc)
    # Format to match the Matlab version, although we don't need to worry
    # about the leap second issue in Python.
    return now.strftime('%Y-%m-%d %H:%M:%S.%f')
