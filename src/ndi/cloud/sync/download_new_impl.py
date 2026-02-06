from .sync_options import SyncOptions
from ..internal.get_cloud_dataset_id_for_local_dataset import get_cloud_dataset_id_for_local_dataset
from .internal.index.index_utils import read_sync_index, update_sync_index
from .internal.document_utils import list_remote_document_ids, list_local_documents
from .internal.download_ndi_documents import download_ndi_documents

def download_new(ndi_dataset, sync_options=None):
    """
    Download new documents (and associated data files) from remote to local.
    """
    if sync_options is None:
        sync_options = SyncOptions()
    elif isinstance(sync_options, dict):
        sync_options = SyncOptions(**sync_options)

    success = True
    error_message = ''
    report = {'downloaded_document_ids': []}

    try:
        if sync_options.Verbose:
            print(f'Syncing dataset "{ndi_dataset.path}". \nWill download new documents from remote.')

        cloud_dataset_id, _ = get_cloud_dataset_id_for_local_dataset(ndi_dataset)
        if sync_options.Verbose:
            print(f'Using Cloud Dataset ID: {cloud_dataset_id}')

        sync_index = read_sync_index(ndi_dataset)
        remote_ids_last_sync = sync_index.get('remoteDocumentIdsLastSync', [])
        if sync_options.Verbose:
            print(f'Read sync index. Last sync recorded {len(remote_ids_last_sync)} remote documents.')

        remote_document_id_map = list_remote_document_ids(cloud_dataset_id, verbose=sync_options.Verbose)
        current_remote_ndi_ids = remote_document_id_map['ndiId']

        # Determine documents to download
        # setdiff in Matlab: unique values in A that are not in B
        # Python: list(set(A) - set(B)) but order might not be preserved.
        # Use list comprehension to preserve order of A if important, but Matlab 'stable' does that.
        # We need indices too.

        # Mapping API IDs to NDI IDs for lookup
        # remote_document_id_map['ndiId'] and ['apiId'] correspond by index

        ndi_ids_to_download = []
        indices_to_download = []

        remote_ids_last_sync_set = set(remote_ids_last_sync)
        for idx, ndi_id in enumerate(current_remote_ndi_ids):
            if ndi_id not in remote_ids_last_sync_set:
                ndi_ids_to_download.append(ndi_id)
                indices_to_download.append(idx)

        if sync_options.Verbose:
            print(f'Found {len(ndi_ids_to_download)} documents added on remote since last sync.')

        if ndi_ids_to_download:
            cloud_api_ids_to_download = [remote_document_id_map['apiId'][i] for i in indices_to_download]

            if sync_options.DryRun:
                print(f'[DryRun] Would download {len(ndi_ids_to_download)} documents from remote.')
                if sync_options.Verbose:
                    for i in range(len(ndi_ids_to_download)):
                        print(f'  [DryRun] - NDI ID: {ndi_ids_to_download[i]} (Cloud Specific ID: {cloud_api_ids_to_download[i]})')
            else:
                if sync_options.Verbose:
                    print(f'Downloading {len(ndi_ids_to_download)} documents...')

                downloaded_docs = download_ndi_documents(
                    cloud_dataset_id,
                    cloud_api_ids_to_download,
                    ndi_dataset,
                    sync_options
                )

                if downloaded_docs:
                    report['downloaded_document_ids'] = [d.document_properties['base']['id'] for d in downloaded_docs]

                if sync_options.Verbose:
                    print(f'Completed downloading {len(ndi_ids_to_download)} documents.')
        else:
            if sync_options.Verbose:
                print('No new documents to download from remote.')

        if not sync_options.DryRun:
            _, final_local_document_ids = list_local_documents(ndi_dataset)

            update_sync_index(
                ndi_dataset,
                cloud_dataset_id,
                local_document_ids=final_local_document_ids,
                remote_document_ids=remote_document_id_map['ndiId']
            )

            if sync_options.Verbose:
                print('Sync index updated.')

        if sync_options.Verbose:
            print(f'Syncing complete for dataset: {ndi_dataset.path}')

    except Exception as e:
        success = False
        error_message = str(e)
        if sync_options.Verbose:
            print(f'Error in downloadNew: {error_message}')
            # raise e # Optionally re-raise

    return success, error_message, report
