import pandas as pd
from did.query import Query

def subject(session):
    """
    Generate a table of all 'subject' documents.

    Args:
        session: ndi.session object.

    Returns:
        tuple: (subject_table, doc_ids)
    """
    query = Query('', 'isa', 'subject')
    docs = session.database_search(query)

    rows = []
    doc_ids = []

    for doc in docs:
        props = doc.document_properties['subject']
        row = props.copy()

        # Add ID for convenience if not present
        row['subject_id'] = doc.id

        rows.append(row)
        doc_ids.append(doc.id)

    subject_table = pd.DataFrame(rows)
    return subject_table, doc_ids
