import warnings
from ndi.fun.doc.diff import diff as doc_diff
from did.query import Query

def diff(session1, session2, verbose=True, recheck_file_report=None):
    """
    Compares two NDI sessions.

    Args:
        session1, session2: ndi.session objects.
        verbose (bool): Print progress.
        recheck_file_report (dict): Previous report to recheck specific files.

    Returns:
        dict: A report structure detailing differences.
    """
    report = {
        'documentsInAOnly': set(),
        'documentsInBOnly': set(),
        'mismatchedDocuments': [],
        'fileDifferences': []
    }

    if recheck_file_report:
        # Recheck logic not fully implemented in this port step
        if verbose:
            print("Re-checking file differences... (Not fully implemented)")
        return report

    # Fetch all documents
    q = Query('base.id', 'regexp', '(.*)')
    d1_docs = session1.database_search(q)
    d2_docs = session2.database_search(q)

    d1_map = {d.id: d for d in d1_docs}
    d2_map = {d.id: d for d in d2_docs}

    d1_ids = set(d1_map.keys())
    d2_ids = set(d2_map.keys())

    report['documentsInAOnly'] = d1_ids - d2_ids
    report['documentsInBOnly'] = d2_ids - d1_ids

    common_ids = d1_ids.intersection(d2_ids)

    if verbose:
        print(f"Found {len(d1_ids)} docs in session1 and {len(d2_ids)} docs in session2.")
        print(f"Comparing {len(common_ids)} common documents...")

    for i, doc_id in enumerate(common_ids):
        if verbose and (i + 1) % 500 == 0:
            print(f"...examined {i + 1} documents...")

        doc1 = d1_map[doc_id]
        doc2 = d2_map[doc_id]

        are_equal, diff_report = doc_diff(doc1, doc2, ignore_fields=['base.session_id'], check_file_list=True)

        if not are_equal:
            report['mismatchedDocuments'].append({
                'id': doc_id,
                'mismatch': ' '.join(diff_report['details'])
            })

        # File comparison logic
        # Note: opening binary docs requires valid file paths and implementation in session/database
        # Simplified for now

    return report
