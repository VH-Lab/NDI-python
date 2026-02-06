import os
import glob
from ndi.common.path_constants import PathConstants

def find_calc_directories():
    """
    Finds all NDI calculator toolbox directories.

    This function scans for installed NDI calculator toolboxes
    that follow the naming convention 'ndicalc-*-python'.

    It determines the search path by navigating three directories up from the
    main NDI toolbox location. This is necessary because the
    toolboxes are typically installed as sibling directories.

    Returns:
        list: A list of strings, where each string is the full
              path to a found calculator directory.
    """
    d = []
    try:
        # Navigate three directories up from the NDI toolbox directory
        # PathConstants.root_folder() is .../src/ndi
        # 1. .../src
        # 2. .../ (repo root)
        # 3. .../.. (parent of repo root)

        base_path = os.path.dirname(os.path.dirname(os.path.dirname(PathConstants.root_folder())))

        if not os.path.isdir(base_path):
            return []

        # Define the search pattern for calculator directories
        # Using glob to match 'ndicalc*-python'
        search_pattern = os.path.join(base_path, 'ndicalc*-python')

        found_dirs = glob.glob(search_pattern)

        # Filter for directories
        d = [p for p in found_dirs if os.path.isdir(p)]

    except Exception as e:
        # Catch any unexpected errors
        print(f"Warning: An error occurred while trying to find calculator directories: {e}")
        d = []

    return d
