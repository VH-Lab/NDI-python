"""
Database Utils Module
*********************
"""
from ..ndi_object import NDI_Object
from functools import wraps


def handle_iter(func):
    @wraps(func)
    def decorator(self, arg):
        try:
            for item in arg:
                func(self, item)
        except TypeError:
            func(self, arg)
    return decorator


def check_ndi_object(func):
    @wraps(func)
    def decorator(self, ndi_object):
        if isinstance(ndi_object, NDI_Object):
            return func(self, ndi_object)
        else:
            raise TypeError(f'\'{ndi_object}\' is not of type \'NDI_Object\'')
    return decorator
