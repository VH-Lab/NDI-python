def delete_remote_documents(cloud_dataset_id, document_ids, verbose=False):
    """
    Deletes documents from the remote cloud dataset.

    Args:
        cloud_dataset_id (str): The cloud dataset ID.
        document_ids (list): A list of cloud document IDs to delete.
        verbose (bool): Whether to print progress messages.

    Returns:
        tuple: (success, deleted_ids)
    """
    from ...api.documents import delete_document

    if not document_ids:
        return True, []

    if verbose:
        print(f'Deleting {len(document_ids)} documents from remote dataset {cloud_dataset_id}...')

    success_all = True
    deleted_ids = []

    for doc_id in document_ids:
        try:
            success, _, _, _ = delete_document(cloud_dataset_id, doc_id)
            if success:
                deleted_ids.append(doc_id)
            else:
                success_all = False
                if verbose:
                    print(f'Failed to delete remote document: {doc_id}')
        except Exception as e:
            success_all = False
            if verbose:
                print(f'Error deleting remote document {doc_id}: {e}')

    if verbose:
        print(f'Deleted {len(deleted_ids)} documents.')

    return success_all, deleted_ids
