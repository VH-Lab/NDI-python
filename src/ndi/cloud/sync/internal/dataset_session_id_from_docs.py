def dataset_session_id_from_docs(documents):
    """
    Extracts the session ID from a list of documents.

    Args:
        documents (list): A list of NDI documents (objects or dicts).

    Returns:
        str: The session ID, or None if not found.
    """
    for doc in documents:
        # Check if doc is dict or object
        if isinstance(doc, dict):
            props = doc
        elif hasattr(doc, 'document_properties'):
            props = doc.document_properties
        else:
            continue

        # Look for 'ndi_session_id' or similar
        # Based on naming convention, session ID might be in 'session' -> 'id'
        if 'session' in props:
            if isinstance(props['session'], dict) and 'id' in props['session']:
                return props['session']['id']
            # Sometimes it might be directly 'session_id' in base?

        if 'base' in props and 'session_id' in props['base']:
             return props['base']['session_id']

        # Or maybe the document itself IS a session document?
        if 'ndi_document' in props and props['ndi_document'].get('type') == 'ndi_session':
             return props.get('id') or props.get('base', {}).get('id')

    return None
