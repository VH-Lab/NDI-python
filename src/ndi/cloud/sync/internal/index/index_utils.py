import os
import json
import datetime

def get_index_filepath(ndi_dataset_path, mode, verbose=True):
    """
    Returns the path to the sync index file.
    """
    sync_dir_path = os.path.join(ndi_dataset_path, '.ndi', 'sync')
    if not os.path.isdir(sync_dir_path):
        if mode == "write":
            if verbose:
                print(f'Creating sync directory: {sync_dir_path}')
            os.makedirs(sync_dir_path)
    return os.path.join(sync_dir_path, 'index.json')

def create_sync_index_struct(local_ndi_ids, remote_ndi_ids):
    """
    Creates the structure for the NDI sync index.
    """
    index_struct = {
        'localDocumentIdsLastSync': local_ndi_ids,
        'remoteDocumentIdsLastSync': remote_ndi_ids,
        'lastSyncTimestamp': datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    return index_struct

def read_sync_index(ndi_dataset, verbose=True):
    """
    Reads the sync index from disk.
    """
    index_path = get_index_filepath(ndi_dataset.path, "read", verbose=verbose)
    if os.path.isfile(index_path):
        with open(index_path, 'r') as f:
            return json.load(f)
    else:
        return {}

def write_sync_index(ndi_dataset, sync_index, verbose=False):
    """
    Writes the sync index to disk.
    """
    index_path = get_index_filepath(ndi_dataset.path, "write", verbose=verbose)
    with open(index_path, 'w') as f:
        json.dump(sync_index, f, indent=4)

def update_sync_index(ndi_dataset, cloud_dataset_id, local_document_ids=None, remote_document_ids=None):
    """
    Updates synchronization index for the dataset.
    """
    if local_document_ids is None:
        from ..document_utils import list_local_documents
        _, local_document_ids = list_local_documents(ndi_dataset)

    if remote_document_ids is None:
        from ..document_utils import list_remote_document_ids
        remote_docs_map = list_remote_document_ids(cloud_dataset_id)
        remote_document_ids = remote_docs_map['ndiId']

    sync_index = create_sync_index_struct(local_document_ids, remote_document_ids)
    write_sync_index(ndi_dataset, sync_index)
