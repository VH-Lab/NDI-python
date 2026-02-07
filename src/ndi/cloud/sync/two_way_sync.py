from .internal.document_utils import list_remote_document_ids, list_local_documents
from .internal.download_ndi_documents import download_ndi_documents
from .internal.delete_local_documents import delete_local_documents
from .internal.delete_remote_documents import delete_remote_documents
from .internal.upload_documents import upload_documents
from .internal.upload_files_for_dataset_documents import upload_files_for_dataset_documents
from .internal.index.index_utils import read_sync_index, update_sync_index
from ..internal.get_cloud_dataset_id_for_local_dataset import get_cloud_dataset_id_for_local_dataset
from .sync_options import SyncOptions

def two_way_sync(ndi_dataset, sync_options=None):
    """
    Performs a two-way synchronization between local and remote datasets.

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
    report = {
        'downloaded_document_ids': [],
        'uploaded_document_ids': [],
        'deleted_local_document_ids': [],
        'deleted_remote_document_ids': []
    }

    try:
        if sync_options.Verbose:
            print(f'Starting two-way sync for dataset "{ndi_dataset.path}"...')

        cloud_dataset_id, _ = get_cloud_dataset_id_for_local_dataset(ndi_dataset)

        # Current State
        remote_docs_map = list_remote_document_ids(cloud_dataset_id, verbose=sync_options.Verbose)
        current_remote_ids = set(remote_docs_map['ndiId'])
        remote_api_ids = remote_docs_map['apiId']

        local_docs, current_local_ids = list_local_documents(ndi_dataset)
        current_local_ids_set = set(current_local_ids)

        # Last Sync State
        sync_index = read_sync_index(ndi_dataset)
        last_remote_ids = set(sync_index.get('remoteDocumentIdsLastSync', []))
        last_local_ids = set(sync_index.get('localDocumentIdsLastSync', []))

        # Calculate Deltas
        added_remote = current_remote_ids - last_remote_ids
        deleted_remote = last_remote_ids - current_remote_ids

        added_local = current_local_ids_set - last_local_ids
        deleted_local = last_local_ids - current_local_ids_set

        # Determine Actions
        to_download = list(added_remote)
        to_upload = list(added_local)

        # Propagate deletions
        # If deleted on remote, delete on local (unless it was just added locally?)
        to_delete_local = list(deleted_remote - added_local)

        # If deleted on local, delete on remote (unless it was just added remotely?)
        to_delete_remote = list(deleted_local - added_remote)

        # Conflict Handling (Intersection of added_remote and added_local)
        conflicts = set(to_download) & set(to_upload)
        if conflicts:
            print(f"Warning: {len(conflicts)} documents added on both sides. Skipping these to avoid overwrite.")
            to_download = list(set(to_download) - conflicts)
            to_upload = list(set(to_upload) - conflicts)
            # Maybe we should download to update local? Or keep local?
            # Keeping local is safer for now.

        if sync_options.Verbose:
            print(f"To Download: {len(to_download)}")
            print(f"To Upload: {len(to_upload)}")
            print(f"To Delete Local: {len(to_delete_local)}")
            print(f"To Delete Remote: {len(to_delete_remote)}")

        if sync_options.DryRun:
            pass # Already printed counts
        else:
            # Execute Local Deletes
            if to_delete_local:
                delete_local_documents(ndi_dataset, to_delete_local)
                report['deleted_local_document_ids'] = to_delete_local

            # Execute Remote Deletes
            if to_delete_remote:
                # Map to API IDs
                api_ids_to_delete = []
                for nid in to_delete_remote:
                    if nid in last_remote_ids: # Was in remote last time
                        # We don't have mapping for deleted remote docs easily if they are gone from current remote
                        # Wait, we want to delete from remote docs that ARE in current remote
                        pass

                # Logic correction: deleted_local means it IS in current_remote (if not deleted there too)
                # but NOT in current_local.
                # So we check if it is in current_remote.
                real_delete_remote = []
                for nid in to_delete_remote:
                    if nid in current_remote_ids:
                        real_delete_remote.append(nid)

                api_ids_to_delete = []
                for nid in real_delete_remote:
                    try:
                        idx = remote_docs_map['ndiId'].index(nid)
                        api_ids_to_delete.append(remote_api_ids[idx])
                    except ValueError:
                        pass

                if api_ids_to_delete:
                    delete_remote_documents(cloud_dataset_id, api_ids_to_delete, verbose=sync_options.Verbose)
                    report['deleted_remote_document_ids'] = real_delete_remote

            # Execute Downloads
            if to_download:
                # Map to API IDs
                api_ids_to_download = []
                for nid in to_download:
                    try:
                        idx = remote_docs_map['ndiId'].index(nid)
                        api_ids_to_download.append(remote_api_ids[idx])
                    except ValueError:
                        pass

                if api_ids_to_download:
                    downloaded = download_ndi_documents(cloud_dataset_id, api_ids_to_download, ndi_dataset, sync_options)
                    if downloaded:
                        report['downloaded_document_ids'] = [d.document_properties['base']['id'] for d in downloaded]

            # Execute Uploads
            if to_upload:
                docs_to_upload = [d for d in local_docs if d.document_properties['base']['id'] in to_upload]
                success_up, uploaded_ids = upload_documents(ndi_dataset, cloud_dataset_id, docs_to_upload, verbose=sync_options.Verbose)
                if success_up:
                    report['uploaded_document_ids'] = uploaded_ids
                    if sync_options.SyncFiles:
                        upload_files_for_dataset_documents(ndi_dataset, cloud_dataset_id, docs_to_upload, verbose=sync_options.Verbose)

            # Update Index
            # New state is roughly current state + downloaded - deleted local
            # But simpler to just list again? Or construct from known changes.
            # Listing again is safer but slower.
            # We can construct expected state.

            new_local = set(current_local_ids) - set(report['deleted_local_document_ids']) | set(report['downloaded_document_ids'])
            new_remote = set(current_remote_ids) - set(report['deleted_remote_document_ids']) | set(report['uploaded_document_ids'])

            update_sync_index(
                ndi_dataset,
                cloud_dataset_id,
                local_document_ids=list(new_local),
                remote_document_ids=list(new_remote)
            )

    except Exception as e:
        success = False
        error_message = str(e)
        if sync_options.Verbose:
            print(f'Error in twoWaySync: {error_message}')
            import traceback
            traceback.print_exc()

    return success, error_message, report
