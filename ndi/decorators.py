from typeguard import typechecked
from inspect import isfunction
from functools import wraps
import ndi.types as T


def typechecked_class(cls: T.Class) -> T.Class:
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


def handle_iter(func):
    """
    Decorator: If passed a list of :term:`NDI object`\ s, it will call func with each one. Otherwise, it will call func(arg) once.

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
