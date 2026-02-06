from ..implementation.datasets.list_datasets import ListDatasets as ListDatasetsImpl

def list_datasets(cloud_organization_id=None):
    """
    User-facing wrapper to list datasets in an organization.

    Args:
        cloud_organization_id: The ID of the organization to query.

    Returns:
        A tuple of (success, answer, api_response, api_url).
    """
    api_call = ListDatasetsImpl(cloud_organization_id=cloud_organization_id)
    return api_call.execute()
