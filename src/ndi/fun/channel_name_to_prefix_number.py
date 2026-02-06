import re

def channel_name_to_prefix_number(channel_name):
    """
    Identifies the prefix and number from a channel name string.
    """
    if not isinstance(channel_name, str):
        raise TypeError("Channel name must be a string.")

    match = re.match(r'([a-zA-Z\s]+)(\d+)', channel_name)
    if not match:
        raise ValueError(f"Could not parse channel name: {channel_name}")

    prefix = match.group(1).strip()
    number = int(match.group(2))

    return prefix, number
