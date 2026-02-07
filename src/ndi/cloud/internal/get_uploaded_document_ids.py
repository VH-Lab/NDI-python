def get_uploaded_document_ids(dataset_id, verbose=False):
    """
    Returns a dictionary of uploaded document IDs from the cloud.

    Args:
        dataset_id (str): The cloud dataset ID.
        verbose (bool): Whether to print progress messages.

    Returns:
        dict: A dictionary with keys 'ndiId' and 'apiId', containing lists of NDI and API document IDs.
    """
    from ..api.documents import list_dataset_documents_all

    if verbose:
        print(f'Fetching complete remote document list for dataset {dataset_id}...')

    success, all_documents, _, _ = list_dataset_documents_all(dataset_id)

    if not success:
        error_msg = all_documents.get('message', 'Unknown error') if isinstance(all_documents, dict) else all_documents
        raise RuntimeError(f"Failed to list remote documents: {error_msg}")

    if not all_documents:
        if verbose:
            print('No remote documents found.')
        return {'ndiId': [], 'apiId': []}

    all_ndi_ids = [doc.get('ndiId') for doc in all_documents]
    all_api_ids = [doc.get('id') for doc in all_documents]

    if verbose:
        print(f'Total remote documents processed: {len(all_ndi_ids)}.')

    return {'ndiId': all_ndi_ids, 'apiId': all_api_ids}
