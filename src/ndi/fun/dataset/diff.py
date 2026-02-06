def diff(dataset1, dataset2):
    """
    Compares two NDI datasets.

    This functionality is similar to ndi.fun.session.diff, as dataset often inherits from session or behaves similarly.
    """
    # Reuse session diff
    from ndi.fun.session.diff import diff as session_diff
    return session_diff(dataset1, dataset2)
