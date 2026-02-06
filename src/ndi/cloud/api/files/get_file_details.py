from ..implementation.files.get_file_details import GetFileDetails as GetFileDetailsImpl

def get_file_details(dataset_id, file_uid):
    """
    User-facing wrapper to get file details.

    Args:
        dataset_id (str): The ID of the dataset.
        file_uid (str): The UID of the file.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = GetFileDetailsImpl(dataset_id, file_uid)
    return api_call.execute()
