def delete_local_documents(ndi_dataset, document_ids):
    """
    Deletes documents from the local dataset.

    Args:
        ndi_dataset (ndi.dataset.Dataset): The local dataset object.
        document_ids (list): A list of document IDs to delete.
    """
    if not document_ids:
        return

    # Check if ndi_dataset has database_rm method
    if hasattr(ndi_dataset, 'database_rm'):
        for doc_id in document_ids:
            try:
                ndi_dataset.database_rm(doc_id)
            except Exception as e:
                print(f"Warning: Failed to delete local document {doc_id}: {e}")
    else:
        # Fallback or error if method is missing?
        # Maybe access database directly if available?
        # But database_rm is the public interface.
        print("Warning: database_rm method not found on dataset object. Cannot delete local documents.")
