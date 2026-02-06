from did.query import Query

def location(S, e):
    """
    Return probe location documents and probe object for an NDI element.

    Args:
        S: ndi.session or ndi.dataset.
        e: ndi.element object or ID string.

    Returns:
        tuple: (probe_locations, probe_obj)
            probe_locations (list): List of probe_location documents.
            probe_obj (ndi.probe.Probe): The probe object.
    """
    # Step 1: get the element object if it's an identifier
    if isinstance(e, str):
        q = Query('base.id', 'exact_string', e)
        element_docs = S.database_search(q)
        if not element_docs:
            raise ValueError(f"Could not find an element with id {e}.")

        # We need a way to convert doc to object.
        # This is typically done via S.query or similar.
        # For now, let's assume we can get it from the doc wrapper or user provided obj
        # But wait, python port might not have full element wrapper logic yet.
        raise NotImplementedError("Converting doc ID to element object not fully supported yet.")

    # Step 2: traverse down to the probe
    current_element = e

    # Check if current_element is a Probe (requires importing Probe class or checking type string)
    # Python doesn't have `isa` in the same way, need isinstance.
    # But circular imports might prevent importing Probe here.
    # We can check class name string or use duck typing.

    def is_probe(obj):
        # Basic check
        return getattr(obj, 'is_probe', False) or 'Probe' in obj.__class__.__name__

    while not is_probe(current_element):
        if hasattr(current_element, 'underlying_element'):
            current_element = current_element.underlying_element
            if current_element is None:
                break
        else:
            break

    # Step 3: we have the probe, assign output
    probe_obj = current_element
    probe_locations = []

    if probe_obj is None or not is_probe(probe_obj):
        return probe_locations, probe_obj

    probe_identifier = probe_obj.id

    # Step 4: query for the locations
    q1 = Query('', 'depends_on', 'probe_id', probe_identifier)
    q2 = Query('', 'isa', 'probe_location')

    probe_locations = S.database_search(q1 & q2)

    return probe_locations, probe_obj
