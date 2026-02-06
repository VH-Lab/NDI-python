from collections import Counter
from did.query import Query

def get_doc_types(session):
    """
    Find all unique document types and their counts in an NDI session.

    Args:
        session: An NDI session object.

    Returns:
        tuple: (doc_types, doc_counts)
            doc_types (list): A list of unique document class names (sorted).
            doc_counts (list): A list of counts corresponding to doc_types.
    """
    query = Query('', 'isa', 'base')
    docs = session.database_search(query)

    doc_classes = [doc.doc_class() for doc in docs]

    counts = Counter(doc_classes)
    sorted_classes = sorted(counts.keys())

    doc_types = sorted_classes
    doc_counts = [counts[c] for c in sorted_classes]

    return doc_types, doc_counts
