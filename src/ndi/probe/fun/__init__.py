import json
from importlib.resources import files

_cached_probe_type_map = None

def get_probe_type_map():
    """
    Returns a dictionary mapping probe types to their corresponding class names.

    This function caches the probe type map to avoid reloading it from the JSON
    file on every call.
    """
    global _cached_probe_type_map
    if _cached_probe_type_map is None:
        _cached_probe_type_map = init_probe_type_map()
    return _cached_probe_type_map

def init_probe_type_map():
    """
    Initializes and returns the probe type map from the JSON file.

    This function reads the `probetype2object.json` file and constructs a
    dictionary mapping probe types to class names.
    """
    json_file_path = files('ndi.resources').joinpath('probetype2object.json')
    with open(json_file_path, 'r') as f:
        data = json.load(f)

    return {item['type']: item['classname'] for item in data}
