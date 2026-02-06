def filename_to_epoch_id(session, filename):
    """
    Finds the epochid associated with a given filename.
    """
    if isinstance(filename, str):
        filename = [filename]

    try:
        if hasattr(session, 'daq_system_load'):
            devs = session.daq_system_load()
        elif hasattr(session, 'daqsystem_load'):
            devs = session.daqsystem_load()
        else:
            raise TypeError("Session object must have daq_system_load method.")
    except AttributeError:
        # Fallback or error
        raise TypeError("Session object must have daq_system_load method.")

    if not isinstance(devs, list):
        devs = [devs]

    result_epoch_ids = [None] * len(filename)

    for dev in devs:
        et = getattr(dev, 'epoch_table', None)
        if et is None and hasattr(dev, 'epochtable'):
             et = dev.epochtable

        if et is None:
            continue

        try:
            iterator = iter(et)
        except TypeError:
            continue

        for e in iterator:
             # underlying_epochs.underlying
             underlying = None

             underlying_epochs = None
             if isinstance(e, dict):
                 underlying_epochs = e.get('underlying_epochs')
             else:
                 underlying_epochs = getattr(e, 'underlying_epochs', None)

             if underlying_epochs:
                 if isinstance(underlying_epochs, dict):
                     underlying = underlying_epochs.get('underlying')
                 else:
                     underlying = getattr(underlying_epochs, 'underlying', None)

             if underlying:
                 if isinstance(underlying, str):
                     underlying = [underlying]

                 # Check matches
                 for i, fname in enumerate(filename):
                     for u_file in underlying:
                         # Case sensitive? Matlab: contains
                         if fname in u_file:
                             e_id = e.get('epoch_id') if isinstance(e, dict) else getattr(e, 'epoch_id', None)
                             result_epoch_ids[i] = e_id

    return result_epoch_ids
