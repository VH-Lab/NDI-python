from did.query import Query

def find_fuid(ndi_obj, fuid):
    """
    Find a document in an NDI dataset or session by its file UID.

    Args:
        ndi_obj (ndi.dataset or ndi.session): An ndi.dataset or ndi.session object to search within.
        fuid (str): The file unique identifier to search for.

    Returns:
        tuple: (doc, filename)
            doc (ndi.document or None): The document object if found, else None.
            filename (str): The filename associated with the FUID, else ''.
    """
    doc = None
    filename = ''

    search_query = Query('base.id', 'regexp', '(.*)')
    all_docs = ndi_obj.database_search(search_query)

    for current_doc in all_docs:
        file_list = current_doc.current_file_list()

        for fname in file_list:
            doc_fuid = current_doc.get_fuid(fname)
            if doc_fuid == fuid:
                doc = current_doc
                filename = fname
                return doc, filename

    return doc, filename
