import hashlib
import os

def md5(file_path):
    """
    Calculates the MD5 checksum of a file.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The 32-character hexadecimal MD5 hash.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
