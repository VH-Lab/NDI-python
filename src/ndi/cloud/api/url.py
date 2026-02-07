import os
from urllib.parse import urljoin

_endpoint_map = None

def get_url(endpoint_name, **kwargs):
    """
    Returns the URL for a named API endpoint.
    """
    global _endpoint_map
    if _endpoint_map is None:
        _init_endpoint_map()

    api_environment = os.getenv('CLOUD_API_ENVIRONMENT', 'prod')

    if api_environment == 'prod':
        api_base_url = "https://api.ndi-cloud.com/v1/"
    elif api_environment == 'dev':
        api_base_url = "https://dev-api.ndi-cloud.com/v1/"
    else:
        raise ValueError(f"Unknown API environment: {api_environment}")

    endpoint_path = _endpoint_map.get(endpoint_name)
    if not endpoint_path:
        raise ValueError(f"Unknown endpoint name: {endpoint_name}")
    endpoint_path = endpoint_path.lstrip('/')

    # Process kwargs to match the expected format
    processed_kwargs = {
        'uid': kwargs.get('file_uid'),
        'datasetId': kwargs.get('dataset_id'),
        'documentId': kwargs.get('document_id'),
        'organizationId': kwargs.get('organization_id') or os.environ.get('NDI_CLOUD_ORGANIZATION_ID'),
        'userId': kwargs.get('user_id'),
        'pageSize': kwargs.get('page_size', 20),
        'page': kwargs.get('page', 1)
    }

    # Filter out None values to avoid issues with f-string formatting
    processed_kwargs = {k: v for k, v in processed_kwargs.items() if v is not None}

    # Use format_map for safe substitution
    try:
        endpoint_path = endpoint_path.format_map(processed_kwargs)
    except KeyError as e:
        raise ValueError(f"Missing required parameter '{e.args[0]}' for endpoint '{endpoint_name}'")


    return urljoin(api_base_url, endpoint_path)

def _init_endpoint_map():
    """
    Initializes the endpoint map.
    """
    global _endpoint_map
    _endpoint_map = {
        "login": "/auth/login",
        "logout": "/auth/logout",
        "resend_confirmation": "/auth/confirmation/resend",
        "verify_user": "/auth/verify",
        "change_password": "/auth/password",
        "reset_password": "/auth/password/forgot",
        "set_new_password": "/auth/password/confirm",
        "create_user": "/users",
        "get_user": "/users/{userId}",
        "get_dataset": "/datasets/{datasetId}",
        "update_dataset": "/datasets/{datasetId}",
        "delete_dataset": "/datasets/{datasetId}",
        "list_datasets": "/organizations/{organizationId}/datasets",
        "create_dataset": "/organizations/{organizationId}/datasets",
        "get_published": "/datasets/published?page={page}&pageSize={pageSize}",
        "get_unpublished": "/datasets/unpublished?page={page}&pageSize={pageSize}",
        "get_file_upload_url": "/datasets/{organizationId}/{datasetId}/files/{uid}",
        "get_file_collection_upload_url": "/datasets/{organizationId}/{datasetId}/files/bulk",
        "get_file_details": "/datasets/{datasetId}/files/{uid}/detail",
        "create_dataset_branch": "/datasets/{datasetId}/branch",
        "get_branches": "/datasets/{datasetId}/branches",
        "submit_dataset": "/datasets/{datasetId}/submit",
        "publish_dataset": "/datasets/{datasetId}/publish",
        "unpublish_dataset": "/datasets/{datasetId}/unpublish",
        "document_count": "/datasets/{datasetId}/document-count",
        "get_document": "/datasets/{datasetId}/documents/{documentId}",
        "update_document": "/datasets/{datasetId}/documents/{documentId}",
        "delete_document": "/datasets/{datasetId}/documents/{documentId}",
        "bulk_delete_documents": "/datasets/{datasetId}/documents/bulk-delete",
        "bulk_upload_documents": "/datasets/{datasetId}/documents/bulk-upload",
        "bulk_download_documents": "/datasets/{datasetId}/documents/bulk-download",
        "list_dataset_documents": "/datasets/{datasetId}/documents?page={page}&pageSize={pageSize}",
        "add_document": "/datasets/{datasetId}/documents",
        "search_datasets": "/datasets/search",
    }
