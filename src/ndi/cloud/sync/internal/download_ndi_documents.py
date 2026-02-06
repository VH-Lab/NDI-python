import os
import tempfile
from ...download.download_utils import download_document_collection, download_dataset_files
from .file_utils import get_file_uids_from_documents, update_file_info_for_local_files, update_file_info_for_remote_files
from .constants import Constants

def download_ndi_documents(cloud_dataset_id, cloud_document_ids, ndi_dataset=None, sync_options=None):
    """
    Downloads a collection of NDI documents and their files.
    """
    if sync_options is None:
        from ..sync_options import SyncOptions
        sync_options = SyncOptions()

    if not cloud_document_ids:
        if sync_options.Verbose:
            print('No document IDs provided to download.')
        return []

    if sync_options.Verbose:
        print(f'Attempting to download {len(cloud_document_ids)} documents...')

    new_ndi_documents = download_document_collection(cloud_dataset_id, cloud_document_ids)

    if not new_ndi_documents:
        print('Warning: No documents were retrieved from the cloud for the given IDs.')
        return []

    if sync_options.Verbose:
        print(f'Successfully retrieved metadata for {len(new_ndi_documents)} documents.')

    if sync_options.SyncFiles:
        if sync_options.Verbose:
            print('SyncFiles is true. Processing associated data files...')

        if ndi_dataset is None:
            root_files_folder = tempfile.gettempdir()
        else:
            root_files_folder = ndi_dataset.path

        files_target_folder = os.path.join(root_files_folder, Constants.FileSyncLocation)

        file_uids_to_download = get_file_uids_from_documents(new_ndi_documents)

        if file_uids_to_download:
            if sync_options.Verbose:
                print(f'Found {len(file_uids_to_download)} unique file UIDs to download for these documents.')
                print(f'Ensuring download directory exists: {files_target_folder}')

            if not os.path.isdir(files_target_folder):
                os.makedirs(files_target_folder)

            download_dataset_files(
                cloud_dataset_id,
                files_target_folder,
                file_uids_to_download,
                verbose=sync_options.Verbose
            )

            if sync_options.Verbose:
                print('Completed downloading data files.')
                print('Updating document file info to point to local files.')
        else:
            if sync_options.Verbose:
                print('No associated files found for these documents, or files already local.')

        processed_documents = []
        for doc in new_ndi_documents:
            processed_documents.append(update_file_info_for_local_files(doc, files_target_folder))
        new_ndi_documents = processed_documents

    else:
        if sync_options.Verbose:
            print('"SyncFiles" option is false. Updating document file info to reflect remote files.')

        processed_documents = []
        for doc in new_ndi_documents:
            processed_documents.append(update_file_info_for_remote_files(doc, cloud_dataset_id))
        new_ndi_documents = processed_documents

    if ndi_dataset is not None:
        if sync_options.Verbose:
            print(f'Adding {len(new_ndi_documents)} processed documents to the local dataset...')
        ndi_dataset.database_add(new_ndi_documents)
        if sync_options.Verbose:
            print('Documents added to the dataset.')

    return new_ndi_documents
