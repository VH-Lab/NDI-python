"""Utilities"""
from typeguard import typechecked
from inspect import isfunction
import re


# Captures "words" in pascal case
pascal_pattern = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')
def pascal_to_snake_case(string):
    """Converts  PascalCase strings to snake_case
    
    :param string: String without whitespace.
    :type string: str
    :return: String in snake case.
    :rtype: str
    """
    return pascal_pattern.sub(r'_\1', string).lower()

def class_to_collection_name(ndi_class):
    """Convert a :class:`ndi.ndi_class` __name__ (PascalCase, singular) to a collection name (snake_case, plural).
    .. note::
        For consistency, collection names are made plural by the addition of an 's'.
    
    :param string: An :class:`ndi.ndi_class` object.
    :type string: :class:`ndi.ndi_class`
    :return: A standardized collection name for the given class.
    :rtype: str
    """
    return f'{pascal_to_snake_case(ndi_class.__name__)}s'

def flatten(nested_list):
    """[summary]
    
    :param nested_list: [description]
    :type nested_list: [type]
    """
    return [ item for l in nested_list for item in l ]

def typecheckedcls(cls):
    """Checks type annotation for class methods

    Class decorator: to be used on class definitions. Class methods can then be annotated and will raise TypeError if arguments do not match types declared by annotation.

    :param cls:
    :type cls: type
    :return: Returns cls with type-check on its methods 
    """
    for attr_name in dir(cls):
        if isfunction(attr := getattr(cls, attr_name)):
            setattr(cls, attr_name, typechecked(attr))
    return cls
