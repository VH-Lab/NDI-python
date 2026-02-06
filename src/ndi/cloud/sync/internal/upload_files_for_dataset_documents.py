import os
import requests
from ...api.files import get_file_upload_url
from ...internal.get_uploaded_file_ids import get_uploaded_file_ids

def upload_files_for_dataset_documents(ndi_dataset, cloud_dataset_id, documents, verbose=False):
    """
    Uploads files associated with the given documents to the cloud dataset.

    Args:
        ndi_dataset (ndi.dataset.Dataset): The local dataset.
        cloud_dataset_id (str): The cloud dataset ID.
        documents (list): List of NDI documents.
        verbose (bool): Whether to print progress messages.

    Returns:
        tuple: (success, uploaded_file_uids)
    """
    if not documents:
        return True, []

    # Get existing remote files to avoid re-uploading
    try:
        remote_file_uids = set(get_uploaded_file_ids(cloud_dataset_id, verbose=verbose))
    except Exception as e:
        if verbose:
            print(f"Warning: Could not fetch remote file list: {e}")
        remote_file_uids = set()

    uploaded_file_uids = []
    success_all = True

    for doc in documents:
        # Access document properties
        if hasattr(doc, 'document_properties'):
            props = doc.document_properties
        elif isinstance(doc, dict):
            props = doc
        else:
            continue

        file_info = props.get('files', {}).get('file_info', [])

        for info in file_info:
            locations = info.get('locations', [])
            file_uid = None
            local_path = None

            # Find local location and UID
            for loc in locations:
                if 'uid' in loc:
                    file_uid = loc['uid']

                # Check for local file path
                # Assuming location_type 'file' or just checking if 'location' is a path
                if loc.get('location_type') == 'file' or loc.get('location_type') == 'local': # 'local' is guess
                    path = loc.get('location')
                    if path:
                        if os.path.isfile(path):
                            local_path = path
                        elif os.path.isfile(os.path.join(ndi_dataset.path, path)):
                            local_path = os.path.join(ndi_dataset.path, path)

            if file_uid and local_path:
                if file_uid in remote_file_uids:
                    if verbose:
                        print(f"File {file_uid} already exists remotely. Skipping.")
                    continue

                if verbose:
                    print(f"Uploading file {file_uid} from {local_path}...")

                try:
                    # Get upload URL
                    success, answer, response, _ = get_file_upload_url(cloud_dataset_id, file_uid)

                    if success:
                        upload_url = answer.get('url') # Assuming API returns 'url'
                        if upload_url:
                            with open(local_path, 'rb') as f:
                                # PUT to presigned URL
                                # Content-Type should match? Or generic?
                                # Usually S3 presigned URLs don't enforce unless signed.
                                # But let's try generic binary.
                                upload_response = requests.put(upload_url, data=f)

                                if upload_response.status_code in [200, 201]:
                                    if verbose:
                                        print(f"Successfully uploaded file {file_uid}.")
                                    uploaded_file_uids.append(file_uid)
                                else:
                                    print(f"Failed to upload content for file {file_uid}. Status: {upload_response.status_code}")
                                    success_all = False
                        else:
                            print(f"Failed to get upload URL for file {file_uid}. Response missing 'url'.")
                            success_all = False
                    else:
                        print(f"Failed to get upload URL for file {file_uid}. API Error: {answer}")
                        success_all = False

                except Exception as e:
                    print(f"Error uploading file {file_uid}: {e}")
                    success_all = False
            elif file_uid and not local_path:
                # File defined but not found locally
                # Maybe strictly a warning?
                # print(f"Warning: File {file_uid} not found locally for document {props.get('base', {}).get('id')}.")
                pass

    return success_all, uploaded_file_uids
