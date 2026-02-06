from ..implementation.datasets.get_dataset import GetDataset as GetDatasetImpl

def get_dataset(dataset_id):
    """
    User-facing wrapper to get dataset details.

    Args:
        dataset_id (str): The ID of the dataset.

    Returns:
        tuple: (success, answer, response, url)
    """
    api_call = GetDatasetImpl(dataset_id)
    return api_call.execute()
