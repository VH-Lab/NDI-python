import os
import requests
import json
import tempfile
import zipfile
import time
from ..api.documents import get_bulk_download_url
from ..api.datasets import get_dataset
from ..api.files import get_file_details
from ...document import Document

def download_document_collection(dataset_id, document_ids=None, timeout=20, chunk_size=2000):
    """
    Download documents using bulk download with chunking.
    """
    if not document_ids:
        # Avoid circular import by importing inside function
        from ...sync.internal.document_utils import list_remote_document_ids
        print('No document IDs provided; fetching all document IDs from the server...')
        id_map = list_remote_document_ids(dataset_id)
        document_ids = id_map['apiId']
        if not document_ids:
            return []

    num_docs = len(document_ids)
    num_chunks = (num_docs + chunk_size - 1) // chunk_size
    document_chunks = [document_ids[i:i + chunk_size] for i in range(0, num_docs, chunk_size)]

    all_document_structs = []
    print(f'Beginning download of {num_docs} documents in {num_chunks} chunk(s).')

    for c, chunk_doc_ids in enumerate(document_chunks, 1):
        print(f'  Processing chunk {c} of {num_chunks} ({len(chunk_doc_ids)} documents)...')

        success, download_url, _, _ = get_bulk_download_url(dataset_id, chunk_doc_ids)
        if not success:
            raise RuntimeError(f"Failed to get bulk download URL for chunk {c}")

        with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
            temp_zip_path = temp_zip.name

        try:
            is_finished = False
            start_time = time.time()

            while not is_finished and (time.time() - start_time) < timeout:
                try:
                    response = requests.get(download_url, stream=True)
                    if response.status_code == 200:
                        with open(temp_zip_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        is_finished = True
                    else:
                        time.sleep(1)
                except Exception:
                    time.sleep(1)

            if not is_finished:
                raise RuntimeError(f"Download failed for chunk {c} after timeout")

            with tempfile.TemporaryDirectory() as extract_dir:
                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

                # Assume one JSON file per chunk as per Matlab logic (unzippedFiles{1})
                # But zip might contain multiple files. Matlab code: jsonFile = unzippedFiles{1}
                # We iterate over extracted files
                for filename in os.listdir(extract_dir):
                    if filename.endswith('.json'):
                        with open(os.path.join(extract_dir, filename), 'r') as f:
                            # Handling potential NaN/Null is skipped for now, assuming standard JSON
                            document_structs = json.load(f)
                            # dropDuplicateDocsFromJsonDecode logic is skipped for now
                            if isinstance(document_structs, list):
                                all_document_structs.extend(document_structs)
                            else:
                                all_document_structs.append(document_structs)
        finally:
            if os.path.exists(temp_zip_path):
                os.remove(temp_zip_path)

    print(f'Download complete. Converting {len(all_document_structs)} structs to NDI documents...')
    documents = [Document(d) for d in all_document_structs]
    print('Processing complete.')
    return documents

def download_dataset_files(cloud_dataset_id, target_folder, file_uuids=None, verbose=True, abort_on_error=True):
    """
    Downloads dataset files from a cloud dataset.
    """
    success, dataset_info, _, _ = get_dataset(cloud_dataset_id)
    if not success:
        raise RuntimeError(f"Failed to get dataset: {dataset_info}")

    if 'files' not in dataset_info and file_uuids is not None:
        raise RuntimeError('No files found in the dataset despite files requested.')

    if 'files' not in dataset_info:
        return

    files = _filter_files_to_download(dataset_info['files'], file_uuids)
    num_files = len(files)

    if verbose:
        print(f'Will download {num_files} files...')

    for i, file_info in enumerate(files, 1):
        if verbose:
            _display_progress(i, num_files)

        file_uid = file_info['uid']
        exists_on_cloud = file_info.get('uploaded', False)

        if not exists_on_cloud:
            print(f'Warning: File with uuid "{file_uid}" does not exist on the cloud, skipping...')
            continue

        target_filepath = os.path.join(target_folder, file_uid)
        if os.path.exists(target_filepath):
            if verbose:
                print(f'File {i} already exists locally, skipping...')
            continue

        success, answer, _, _ = get_file_details(cloud_dataset_id, file_uid)
        if not success:
            print(f"Warning: Failed to get file details: {answer}")
            continue

        download_url = answer.get('downloadUrl')
        if not download_url:
             print(f"Warning: No download URL for file {file_uid}")
             continue

        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            with open(target_filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except Exception as e:
            if abort_on_error:
                raise e
            else:
                print(f"Warning: Download failed for file {i}: {e}")

    if verbose:
        print('File download complete.')

def _filter_files_to_download(files, file_uuids):
    if file_uuids is not None:
        # Assuming file_uuids is a list of strings
        # Filter files where uid is in file_uuids
        filtered_files = [f for f in files if f['uid'] in file_uuids]
        return filtered_files
    return files

def _display_progress(current_file_number, total_file_number):
    percent_finished = round((current_file_number / total_file_number) * 100)
    print(f'Downloading file {current_file_number} of {total_file_number} ({percent_finished}% complete) ...')
