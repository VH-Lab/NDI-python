import copy

def diff(doc1, doc2, ignore_fields=None, check_file_list=True, check_files=False, session1=None, session2=None):
    """
    Compare two NDI documents for equality.

    Args:
        doc1, doc2: ndi.document objects to compare.
        ignore_fields (list): Fields to ignore (default: ['base.session_id']).
        check_file_list (bool): Check if file lists match (default: True).
        check_files (bool): Check binary content (default: False).
        session1, session2: ndi.session objects (required if check_files=True).

    Returns:
        tuple: (are_equal, report)
            are_equal (bool): True if documents match.
            report (dict): Details of differences.
    """
    if ignore_fields is None:
        ignore_fields = ['base.session_id']

    if check_files:
        if session1 is None or session2 is None:
            raise ValueError('If check_files is True, session1 and session2 must be provided.')

    are_equal = True
    details = []

    # Deep copy properties to avoid modifying originals
    props1 = copy.deepcopy(doc1.document_properties)
    props2 = copy.deepcopy(doc2.document_properties)

    # 1. Remove ignored fields
    for field in ignore_fields:
        parts = field.split('.')
        if len(parts) == 1:
            props1.pop(field, None)
            props2.pop(field, None)
        elif len(parts) == 2:
            if parts[0] in props1 and isinstance(props1[parts[0]], dict):
                props1[parts[0]].pop(parts[1], None)
            if parts[0] in props2 and isinstance(props2[parts[0]], dict):
                props2[parts[0]].pop(parts[1], None)

    # 2. Handle 'depends_on' (Order Independent)
    dep1 = props1.pop('depends_on', [])
    dep2 = props2.pop('depends_on', [])

    if dep1 or dep2:
        if len(dep1) != len(dep2):
            are_equal = False
            details.append(f"Number of dependencies differs: {len(dep1)} vs {len(dep2)}.")
        else:
            # Sort by name
            dep1_sorted = sorted(dep1, key=lambda x: x.get('name', ''))
            dep2_sorted = sorted(dep2, key=lambda x: x.get('name', ''))

            if dep1_sorted != dep2_sorted:
                are_equal = False
                details.append("Dependencies do not match.")

    # 3. Handle 'files' (Order Independent List Check)
    files1 = props1.pop('files', {})
    files2 = props2.pop('files', {})

    if check_file_list:
        f_list1 = files1.get('file_list', [])
        f_list2 = files2.get('file_list', [])

        # Ensure lists are sorted
        if sorted(f_list1) != sorted(f_list2):
            are_equal = False
            details.append("File lists do not match.")

    # 4. Compare remaining properties
    if props1 != props2:
        are_equal = False
        details.append("Document properties do not match.")

    # 5. Check binary file content if requested
    if check_files:
        # Not fully implemented yet due to missing binary comparison utilities
        # and session.database_openbinarydoc implementation details in Python port.
        details.append("Binary file comparison requested but not fully implemented in Python port.")
        # Stub implementation
        pass

    report = {'mismatch': not are_equal, 'details': details}
    return are_equal, report
