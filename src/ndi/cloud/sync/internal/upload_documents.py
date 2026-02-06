from ...api.documents import add_document

def upload_documents(ndi_dataset, cloud_dataset_id, documents, verbose=False):
    """
    Uploads document metadata to the cloud.

    Args:
        ndi_dataset (ndi.dataset.Dataset): Local dataset.
        cloud_dataset_id (str): Cloud dataset ID.
        documents (list): List of NDI documents to upload.
        verbose (bool): Verbosity.

    Returns:
        tuple: (success, uploaded_ids)
    """
    if not documents:
        return True, []

    if verbose:
        print(f"Uploading {len(documents)} documents to cloud dataset {cloud_dataset_id}...")

    success_all = True
    uploaded_ids = []

    for doc in documents:
        # doc is an object or dict?
        # add_document expects dict (json structure)
        if hasattr(doc, 'document_properties'):
            doc_data = doc.document_properties
        elif isinstance(doc, dict):
            doc_data = doc
        else:
            # Maybe it has a method to get properties?
            # Assuming dict or properties attribute for now.
            print(f"Warning: Unknown document format for upload: {type(doc)}")
            continue

        try:
            # Check if doc has 'base.id'
            doc_id = doc_data.get('base', {}).get('id', 'unknown')

            success, answer, _, _ = add_document(cloud_dataset_id, doc_data)

            if success:
                uploaded_ids.append(doc_id)
            else:
                # If 409 Conflict (already exists), we might treat as success or ignore?
                # But here we are mirroring/uploading new.
                print(f"Failed to upload document {doc_id}: {answer}")
                success_all = False
        except Exception as e:
            print(f"Error uploading document: {e}")
            success_all = False

    if verbose:
        print(f"Uploaded {len(uploaded_ids)} documents.")

    return success_all, uploaded_ids
