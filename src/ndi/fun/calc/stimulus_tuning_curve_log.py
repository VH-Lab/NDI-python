from did.query import Query

def stimulus_tuning_curve_log(S, doc):
    """
    Retrieve stimulus_tuningcurve log string from dependent document.

    Args:
        S: ndi.session object.
        doc: ndi.document object.

    Returns:
        str: The log string.
    """
    log_str = ''

    try:
        stim_tune_doc_id = doc.dependency_value('stimulus_tuningcurve_id')
    except Exception:
        # If dependency not found
        return log_str

    q1 = Query('base.id', 'exact_string', stim_tune_doc_id)
    q2 = Query('', 'isa', 'tuningcurve_calc')

    stim_tune_doc = S.database_search(q1 & q2)

    if stim_tune_doc:
        props = stim_tune_doc[0].document_properties.get('tuningcurve_calc', {})
        log_str = props.get('log', '')

    return log_str
