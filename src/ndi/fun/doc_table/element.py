import pandas as pd
from did.query import Query

def element(session):
    """
    Generate a table of all 'element' documents in a session/dataset.

    Args:
        session: ndi.session object.

    Returns:
        tuple: (element_table, doc_ids)
            element_table (pd.DataFrame): Table of element info.
            doc_ids (list): List of document IDs.
    """
    query = Query('', 'isa', 'element')
    docs = session.database_search(query)

    rows = []
    doc_ids = []

    for doc in docs:
        props = doc.document_properties['element']

        # Flatten basic properties
        row = props.copy()

        # Handle direct_recording if present (it's a struct/dict)
        # We might want to flatten it or keep as dict.
        # Matlab flattenstruct2table typically flattens one level.

        rows.append(row)
        doc_ids.append(doc.id)

    element_table = pd.DataFrame(rows)
    return element_table, doc_ids
