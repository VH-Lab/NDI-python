from ...api.documents import list_dataset_documents_all
from ....query import Query

def list_remote_document_ids(cloud_dataset_id, verbose=False):
    """
    List all NDI and API document IDs from a remote dataset.
    """
    if verbose:
        print(f'Fetching complete remote document list for dataset {cloud_dataset_id}...')

    success, all_documents, response, _ = list_dataset_documents_all(cloud_dataset_id)

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

def list_local_documents(ndi_dataset):
    """
    List documents in local dataset.
    """
    # Assuming ndi_dataset has database_search method and Query class is available
    documents = ndi_dataset.database_search(Query('', 'isa', 'base'))
    document_ids = [doc.document_properties['base']['id'] for doc in documents]
    return documents, document_ids
