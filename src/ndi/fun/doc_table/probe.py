import pandas as pd
from did.query import Query

def probe(session):
    """
    Generate a table of all 'probe' documents.

    Args:
        session: ndi.session object.

    Returns:
        tuple: (probe_table, doc_ids)
    """
    query = Query('', 'isa', 'probe')
    docs = session.database_search(query)

    rows = []
    doc_ids = []

    for doc in docs:
        props = doc.document_properties['probe']
        row = props.copy()
        rows.append(row)
        doc_ids.append(doc.id)

    probe_table = pd.DataFrame(rows)
    return probe_table, doc_ids
