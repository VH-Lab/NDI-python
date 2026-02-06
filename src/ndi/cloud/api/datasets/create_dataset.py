from ..implementation.datasets.create_dataset import CreateDataset as CreateDatasetImpl

def create_dataset(dataset_info, organization_id=None):
    """
    User-facing wrapper to create a dataset.

    Args:
        dataset_info (dict): The dataset information.
        organization_id (str, optional): Organization ID.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = CreateDatasetImpl(dataset_info, organization_id)
    return api_call.execute()
