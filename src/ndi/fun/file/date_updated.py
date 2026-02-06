import os
import datetime

def date_updated(file_path):
    """
    Gets the last modification date of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        datetime.datetime: The last modification time. Returns None if it cannot be determined.
    """
    if not os.path.exists(file_path):
        return None

    return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
