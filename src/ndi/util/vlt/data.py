import numpy as np

def emptystruct(*args):
    """
    Creates an empty dictionary with the given fieldnames.

    :param args: The fieldnames for the dictionary.
    :return: A dictionary with the given fieldnames and empty values.
    """
    return {arg: None for arg in args}

def eqlen(x, y):
    """
    Returns True if objects to compare are equal and have same size.
    """
    if sizeeq(x, y):
        return eqtot(x, y)
    return False

def sizeeq(x, y):
    """
    Determines if size of two variables is same.
    """
    try:
        return np.shape(x) == np.shape(y)
    except:
        return len(x) == len(y)

def eqtot(x, y):
    """
    Returns True if all elements are equal.
    """
    return np.array_equal(x, y)

def celloritem(var, index=0, useindexforvar=False):
    """
    Returns the ith element of a list, or a single item.
    """
    if isinstance(var, list):
        return var[index]
    else:
        if useindexforvar:
            return var[index]
        else:
            return var

def structmerge(s1, s2):
    """
    Merges two dictionaries, with values from the second dictionary
    overwriting the first.
    """
    return {**s1, **s2}

def flattenstruct2table(s):
    """
    Flattens a dictionary to a table-like structure.
    """
    # This is a simplified implementation. A more robust version
    # would handle nested dictionaries and lists of dictionaries.
    return s

import hashlib
import json

def hashmatlabvariable(v):
    """
    Computes a hash of a variable, similar to the Matlab version.
    """
    # Convert the variable to a string representation.
    # For dictionaries, we'll sort the keys to ensure consistency.
    s = json.dumps(v, sort_keys=True)
    return hashlib.sha256(s.encode('utf-8')).hexdigest()
