import importlib

def ndi_document2ndi_object(ndi_document_obj, ndi_session_obj):
    if not isinstance(ndi_document_obj, dict):
        # Assuming it's an ID to be looked up
        mydoc = ndi_session_obj.database_search(Query('base.id', 'exact_string', ndi_document_obj, ''))
        if len(mydoc) == 1:
            ndi_document_obj = mydoc[0]
        else:
            raise ValueError("NDI_DOCUMENT_OBJ must be of type dict or an ID of a valid ndi.document.")

    classname = ndi_document_obj['document_class']['class_name']

    doc_string = 'ndi_document_'
    index = classname.find(doc_string)

    if index != -1:
        obj_parent_string = classname[index + len(doc_string):]
    else:
        obj_parent_string = classname

    if obj_parent_string not in ndi_document_obj:
        raise ValueError(f"NDI_DOCUMENT_OBJ does not have a '{obj_parent_string}' field.")
    else:
        obj_struct = ndi_document_obj[obj_parent_string]
        obj_string = obj_struct[f'ndi_{obj_parent_string}_class']

    # dynamically import the class
    parts = obj_string.split('.')
    module_name = '.'.join(parts[:-1])
    class_name = parts[-1]

    TheClass = getattr(importlib.import_module(module_name), class_name)

    return TheClass(ndi_session_obj, ndi_document_obj)
