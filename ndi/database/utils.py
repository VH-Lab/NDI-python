"""
Database Utils Module
*********************
"""
from ..ndi_object import NDI_Object
from functools import wraps


def handle_iter(func):
    """
    Decorator: meant to work with :func:`check_ndi_object`. If passed a list of :term:`NDI object`\ s, it will call func with each one. Otherwise, it will call func(arg) once.
    
    :param func: The wrapped function.
    :type func: function

    :param arg: The first argument passed to the wrapped function.
    :type arg: List<:term:`NDI object`> | :term:`NDI object`

    :rtype: None
    """
    @wraps(func)
    def decorator(self, arg):
        try:
            for item in arg:
                func(self, item)
        except TypeError:
            func(self, arg)
    return decorator


def check_ndi_object(func):
    """.. currentmodule:: ndi.ndi_object
    Decorator: meant to prevent :class:`NDI_Object` database :term:`CRUD` methods from being called with non-standard input. Throws an error if the first argument passed to wrapped function is not an :term:`NDI object`.
    
    :param func: The wrapped function.
    :type func: function

    :param ndi_object: The first argument passed to the wrapped function.
    :type ndi_object: :term:`NDI object`

    :raises TypeError: '{ndi_object}' is not an instance of an \'NDI_Object\' child class.
    :return: func(ndi_object)
    """
    @wraps(func)
    def decorator(self, ndi_object):
        if isinstance(ndi_object, NDI_Object):
            return func(self, ndi_object)
        else:
            raise TypeError(f'\'{ndi_object}\' is not an instance of an \'NDI_Object\' child class.')
    return decorator

def check_ndi_class(func):
    """.. currentmodule:: ndi.ndi_object
    Decorator: meant to prevent :class:`NDI_Object` collection :term:`CRUD` methods from being called with non-standard input. Throws an error if the first argument passed to wrapped function is not the correct :term:`NDI class`.

    :param func: The wrapped function.
    :type func: function

    :param ndi_object: The first argument passed to the wrapped function.
    :type ndi_object: :term:`NDI object`

    :raises TypeError: \'{ndi_object}\' is not an instance of \'{self.ndi_class}\'.
    :return: func(ndi_object)
    """
    @wraps(func)
    def decorator(self, ndi_object):
        if isinstance(ndi_object, self.ndi_class):
            return func(self, ndi_object)
        else:
            raise TypeError(f'\'{ndi_object}\' is not an instance of \'{self.ndi_class}\'')
    return decorator

def listify(func):
    @wraps(func)
    def decorator(self, arg, *args, **kwargs):
        if not isinstance(arg, list):
            func(self, [arg], *args, **kwargs)
        else:
            func(self, arg, *args, **kwargs)
    return decorator

def check_ndi_objects(func):
    @wraps(func)
    def decorator(self, ndi_objects, *args, **kwargs):
        if len(ndi_objects):
            for item in ndi_objects:
                if not isinstance(item, NDI_Object):
                    raise TypeError(f'\'{item}\' is not an instance of an \'NDI_Object\' child class.')
            func(self, ndi_objects, *args, **kwargs)
    return decorator
