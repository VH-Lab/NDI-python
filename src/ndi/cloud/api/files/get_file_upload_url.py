from ..implementation.files.get_file_upload_url import GetFileUploadURL as GetFileUploadURLImpl

def get_file_upload_url(dataset_id, file_uid, organization_id=None):
    """
    Gets the upload URL for a file in a dataset.

    Args:
        dataset_id (str): The ID of the dataset.
        file_uid (str): The UID of the file.
        organization_id (str, optional): The ID of the organization.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = GetFileUploadURLImpl(dataset_id, file_uid, organization_id)
    return api_call.execute()
