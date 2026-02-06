def get_uploaded_file_ids(dataset_id, verbose=False):
    """
    Returns a list of uploaded file IDs from the cloud.

    Args:
        dataset_id (str): The cloud dataset ID.
        verbose (bool): Whether to print progress messages.

    Returns:
        list: A list of unique file UIDs.
    """
    from ..api.documents import list_dataset_documents_all

    if verbose:
        print(f'Listing uploaded files for dataset {dataset_id}...')

    success, all_documents, _, _ = list_dataset_documents_all(dataset_id)

    if not success:
        error_msg = all_documents.get('message', 'Unknown error') if isinstance(all_documents, dict) else all_documents
        raise RuntimeError(f"Failed to list remote documents for files: {error_msg}")

    file_uids = set()
    if all_documents:
        for document in all_documents:
            # Assuming document structure from cloud: properties are usually top-level or under 'document_properties' depending on API
            # Cloud usually returns the document object itself as dict
            # Check if 'files' property exists
            file_info = document.get('files', {}).get('file_info', [])
            for info in file_info:
                locations = info.get('locations', [])
                for location in locations:
                    uid = location.get('uid')
                    if uid:
                        file_uids.add(uid)

    if verbose:
        print(f'Found {len(file_uids)} unique file UIDs.')

    return list(file_uids)
