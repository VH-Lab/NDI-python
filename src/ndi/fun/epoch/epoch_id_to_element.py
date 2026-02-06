def epoch_id_to_element(session, epoch_id, name='', type=''):
    """
    Find an NDI element given an epochid.

    Args:
        session: An NDI session object.
        epoch_id (str or list of str): The unique identifier(s) of the epoch(s) to find.
        name (str): Optional. Restricts search to elements with this name.
        type (str): Optional. Restricts search to elements of this type.

    Returns:
        list: A list of NDI element object(s) associated that contain the epoch(s).
    """
    if isinstance(epoch_id, str):
        epoch_id = [epoch_id]

    # Get elements from the session
    if hasattr(session, 'get_elements'):
        elements = session.get_elements()
    elif hasattr(session, 'getelements'):
        elements = session.getelements()
    else:
        raise TypeError("Session object must have get_elements method.")

    # Filter elements
    if name:
        elements = [e for e in elements if getattr(e, 'name', '') == name]
    if type:
        elements = [e for e in elements if getattr(e, 'type', '') == type]

    result_elements = [None] * len(epoch_id)

    for elem in elements:
        et = getattr(elem, 'epoch_table', None)
        if hasattr(elem, 'epochtable'): # fallback
             et = elem.epochtable

        if et is None:
            continue

        # Iterate through epoch table
        # Assuming et is a list-like of dicts or objects with epoch_id
        try:
            iterator = iter(et)
        except TypeError:
            continue

        for e in iterator:
            e_id = None
            if isinstance(e, dict):
                e_id = e.get('epoch_id')
            else:
                e_id = getattr(e, 'epoch_id', None)

            if e_id:
                 # Check if this e_id matches any in our list (case insensitive)
                 for i, search_id in enumerate(epoch_id):
                     if str(search_id).lower() == str(e_id).lower():
                         result_elements[i] = elem

    return result_elements
