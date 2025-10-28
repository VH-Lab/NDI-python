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
