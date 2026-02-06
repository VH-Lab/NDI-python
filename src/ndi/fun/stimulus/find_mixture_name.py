import json
import os
import pandas as pd

def find_mixture_name(mixture_dictionary_path, mixture):
    """
    Identifies matching mixture names from a dictionary.

    Args:
        mixture_dictionary_path (str): Path to JSON dictionary.
        mixture (dict or list of dict or pd.DataFrame): Mixture to match.

    Returns:
        list: Matching names.
    """
    if not os.path.isfile(mixture_dictionary_path):
        raise FileNotFoundError(f"File not found: {mixture_dictionary_path}")

    with open(mixture_dictionary_path, 'r') as f:
        mixture_dictionary = json.load(f)

    mixture_names = list(mixture_dictionary.keys())

    if isinstance(mixture, pd.DataFrame):
        mixture = mixture.to_dict('records')

    if isinstance(mixture, dict):
        mixture = [mixture]

    matching_names = []

    for name in mixture_names:
        current_dict_entry = mixture_dictionary[name]

        if isinstance(current_dict_entry, dict):
            current_dict_entry = [current_dict_entry]

        # Check if all elements in dictionary entry are present in mixture
        entry_match = True
        for dict_elem in current_dict_entry:
            # Must find a match in mixture list
            found = False
            for mix_elem in mixture:
                # Compare fields
                # keys: ontologyName, name, value, ontologyUnit, unitName
                # Note: value might be float, need tolerance? Matlab uses eq (==)
                if (dict_elem.get('ontologyName') == mix_elem.get('ontologyName') and
                    dict_elem.get('name') == mix_elem.get('name') and
                    dict_elem.get('value') == mix_elem.get('value') and
                    dict_elem.get('ontologyUnit') == mix_elem.get('ontologyUnit') and
                    dict_elem.get('unitName') == mix_elem.get('unitName')):
                    found = True
                    break
            if not found:
                entry_match = False
                break

        if entry_match:
            matching_names.append(name)

    return matching_names
