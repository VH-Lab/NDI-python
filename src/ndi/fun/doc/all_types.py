import os
import glob
from ndi.common.path_constants import PathConstants
from ndi.fun.find_calc_directories import find_calc_directories

def all_types():
    """
    Finds all unique document types available in the NDI system.

    Returns:
        list: A sorted list of unique document type names.
    """
    json_docs = []

    # Check DocumentFolder
    # Assuming standard location
    doc_folder = os.path.join(PathConstants.common_folder(), 'database_documents')
    if os.path.isdir(doc_folder):
        json_docs.extend(glob.glob(os.path.join(doc_folder, '*.json')))

    # Check CalcDoc
    calc_dirs = find_calc_directories()

    for d in calc_dirs:
        calc_doc_path = os.path.join(d, 'ndi_common', 'database_documents')
        if os.path.isdir(calc_doc_path):
            json_docs.extend(glob.glob(os.path.join(calc_doc_path, '*.json')))

    doc_types = set()
    for f in json_docs:
        filename = os.path.basename(f)
        if not filename.startswith('.'):
            name, ext = os.path.splitext(filename)
            doc_types.add(name)

    return sorted(list(doc_types))
