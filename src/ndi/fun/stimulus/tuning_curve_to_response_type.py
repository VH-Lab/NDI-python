from did.query import Query

def tuning_curve_to_response_type(S, doc):
    """
    Get the response type ('mean', 'F1', etc) of a tuning curve document.

    Args:
        S: ndi.session object.
        doc: ndi.document object.

    Returns:
        tuple: (response_type, stim_response_scalar_doc)
    """
    response_type = ''
    stim_response_scalar_doc = None

    dependency_list_to_check = ['stimulus_response_scalar_id', 'stimulus_tuningcurve_id']
    dependency_action = ['finish', 'recursive']

    for i, dep_name in enumerate(dependency_list_to_check):
        d = doc.dependency_value(dep_name, error_if_not_found=False)
        if d:
            q_doc = Query('base.id', 'exact_string', d)
            newdoc = S.database_search(q_doc)
            if len(newdoc) != 1:
                raise RuntimeError(f"Could not find dependent doc {d}.")

            action = dependency_action[i]
            if action == 'recursive':
                return tuning_curve_to_response_type(S, newdoc[0])
            elif action == 'finish':
                try:
                    props = newdoc[0].document_properties['stimulus_response_scalar']
                    response_type = props['response_type']
                    stim_response_scalar_doc = newdoc[0]
                    return response_type, stim_response_scalar_doc
                except KeyError:
                    raise RuntimeError("Could not find field 'response_type' in document.")
            else:
                raise ValueError("Unknown action type")

    return response_type, stim_response_scalar_doc
