from .internal.document_utils import list_remote_document_ids, list_local_documents
from .internal.delete_remote_documents import delete_remote_documents
from .internal.upload_documents import upload_documents
from .internal.upload_files_for_dataset_documents import upload_files_for_dataset_documents
from .internal.index.index_utils import update_sync_index
from ..internal.get_cloud_dataset_id_for_local_dataset import get_cloud_dataset_id_for_local_dataset
from .sync_options import SyncOptions

def mirror_to_remote(ndi_dataset, sync_options=None):
    """
    Mirrors the local dataset to the remote dataset.
    This will delete remote documents that are not present locally,
    and upload documents/files from the local dataset that are missing remotely.

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
    report = {'uploaded_document_ids': [], 'deleted_document_ids': []}

    try:
        if sync_options.Verbose:
            print(f'Mirroring to remote for dataset "{ndi_dataset.path}"...')

        cloud_dataset_id, _ = get_cloud_dataset_id_for_local_dataset(ndi_dataset)

        # List remote documents
        remote_docs_map = list_remote_document_ids(cloud_dataset_id, verbose=sync_options.Verbose)
        remote_ndi_ids = set(remote_docs_map['ndiId'])
        remote_api_ids = remote_docs_map['apiId']

        # List local documents
        local_docs, local_ndi_ids = list_local_documents(ndi_dataset)
        local_ndi_ids_set = set(local_ndi_ids)

        # Calculate differences
        to_delete_remote_ndi = list(remote_ndi_ids - local_ndi_ids_set)
        to_upload_local_ndi = list(local_ndi_ids_set - remote_ndi_ids)

        # Find API IDs for remote deletion
        to_delete_remote_api = []
        for ndi_id in to_delete_remote_ndi:
            try:
                idx = remote_docs_map['ndiId'].index(ndi_id)
                to_delete_remote_api.append(remote_api_ids[idx])
            except ValueError:
                pass

        # Find local objects for upload
        to_upload_docs = []
        for doc in local_docs:
            # Assuming doc has id or we map by index
            # list_local_documents returns (docs, ids) in sync
            doc_id = doc.document_properties['base']['id']
            if doc_id in to_upload_local_ndi:
                to_upload_docs.append(doc)

        if sync_options.Verbose:
            print(f'Found {len(to_delete_remote_ndi)} documents to delete remotely.')
            print(f'Found {len(to_upload_local_ndi)} documents to upload from local.')

        if sync_options.DryRun:
            print('[DryRun] Would delete remote documents:', to_delete_remote_ndi)
            print('[DryRun] Would upload local documents:', to_upload_local_ndi)
        else:
            # Delete remote
            if to_delete_remote_api:
                delete_remote_documents(cloud_dataset_id, to_delete_remote_api, verbose=sync_options.Verbose)
                report['deleted_document_ids'] = to_delete_remote_ndi

            # Upload local
            if to_upload_docs:
                success_upload, uploaded_ids = upload_documents(ndi_dataset, cloud_dataset_id, to_upload_docs, verbose=sync_options.Verbose)
                if success_upload:
                    report['uploaded_document_ids'] = uploaded_ids

                    if sync_options.SyncFiles:
                        upload_files_for_dataset_documents(ndi_dataset, cloud_dataset_id, to_upload_docs, verbose=sync_options.Verbose)

            # Update index
            update_sync_index(
                ndi_dataset,
                cloud_dataset_id,
                local_document_ids=list(local_ndi_ids),
                remote_document_ids=list(set(remote_ndi_ids) - set(to_delete_remote_ndi) | set(report['uploaded_document_ids']))
            )

    except Exception as e:
        success = False
        error_message = str(e)
        if sync_options.Verbose:
            print(f'Error in mirrorToRemote: {error_message}')

    return success, error_message, report
