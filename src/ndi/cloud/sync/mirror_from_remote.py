from .internal.document_utils import list_remote_document_ids, list_local_documents
from .internal.download_ndi_documents import download_ndi_documents
from .internal.delete_local_documents import delete_local_documents
from .internal.index.index_utils import update_sync_index
from ..internal.get_cloud_dataset_id_for_local_dataset import get_cloud_dataset_id_for_local_dataset
from .sync_options import SyncOptions

def mirror_from_remote(ndi_dataset, sync_options=None):
    """
    Mirrors the remote dataset to the local dataset.
    This will delete local documents that are not present in the remote dataset,
    and download documents from the remote dataset that are missing locally.

    Args:
        ndi_dataset (ndi.dataset.Dataset): The local dataset.
        sync_options (SyncOptions, optional): Sync options.

    Returns:
        tuple: (success, error_message, report)
    """
    if sync_options is None:
        sync_options = SyncOptions()

    success = True
    error_message = ''
    report = {'downloaded_document_ids': [], 'deleted_document_ids': []}

    try:
        if sync_options.Verbose:
            print(f'Mirroring from remote for dataset "{ndi_dataset.path}"...')

        cloud_dataset_id, _ = get_cloud_dataset_id_for_local_dataset(ndi_dataset)

        # List remote documents
        remote_docs_map = list_remote_document_ids(cloud_dataset_id, verbose=sync_options.Verbose)
        remote_ndi_ids = set(remote_docs_map['ndiId'])
        remote_api_ids = remote_docs_map['apiId']

        # List local documents
        _, local_ndi_ids = list_local_documents(ndi_dataset)
        local_ndi_ids_set = set(local_ndi_ids)

        # Calculate differences
        to_delete = list(local_ndi_ids_set - remote_ndi_ids)
        to_download_ndi = list(remote_ndi_ids - local_ndi_ids_set)

        # Find API IDs for download
        to_download_api = []
        for ndi_id in to_download_ndi:
            try:
                idx = remote_docs_map['ndiId'].index(ndi_id)
                to_download_api.append(remote_api_ids[idx])
            except ValueError:
                pass

        if sync_options.Verbose:
            print(f'Found {len(to_delete)} documents to delete locally.')
            print(f'Found {len(to_download_ndi)} documents to download from remote.')

        if sync_options.DryRun:
            print('[DryRun] Would delete local documents:', to_delete)
            print('[DryRun] Would download remote documents:', to_download_ndi)
        else:
            # Delete local
            if to_delete:
                delete_local_documents(ndi_dataset, to_delete)
                report['deleted_document_ids'] = to_delete

            # Download remote
            if to_download_api:
                downloaded_docs = download_ndi_documents(
                    cloud_dataset_id,
                    to_download_api,
                    ndi_dataset,
                    sync_options
                )
                if downloaded_docs:
                    report['downloaded_document_ids'] = [doc.document_properties['base']['id'] for doc in downloaded_docs]

            # Update index
            update_sync_index(
                ndi_dataset,
                cloud_dataset_id,
                local_document_ids=list(set(local_ndi_ids) - set(to_delete) | set(report['downloaded_document_ids'])),
                remote_document_ids=list(remote_ndi_ids)
            )

    except Exception as e:
        success = False
        error_message = str(e)
        if sync_options.Verbose:
            print(f'Error in mirrorFromRemote: {error_message}')

    return success, error_message, report
