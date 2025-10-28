from ..implementation.datasets.get_published import GetPublished as GetPublishedImpl

def get_published(page=1, page_size=20):
    """
    User-facing wrapper to get published datasets from NDI Cloud.

    Args:
        page: The page number of results to retrieve.
        page_size: The number of results per page.

    Returns:
        A tuple of (success, answer, api_response, api_url).
    """
    api_call = GetPublishedImpl(page=page, page_size=page_size)
    return api_call.execute()
