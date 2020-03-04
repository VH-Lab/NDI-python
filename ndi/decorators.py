from __future__ import annotations
from functools import wraps
import ndi.types as T

def handle_iter(func: T.Callable) -> T.Callable:
    """
    Decorator: If passed a list of :term:`NDI object`\ s, it will call func with each one. Otherwise, it will call func(arg) once.

    :param func: The wrapped function.
    :type func: function

    :param arg: The first argument passed to the wrapped function.
    :type arg: List<:term:`NDI object`> | :term:`NDI object`

    :rtype: None
    """
    @wraps(func)
    def decorator(self, arg: T.Any) -> None:
        if isinstance(arg, list):
            for item in arg:
                func(self, item)
        else:
            func(self, arg)
    return decorator


def handle_lists(
        func: T.Callable[ [ T.Self, T.Foo ], T.Bar]
    ) -> T.Callable[ [ T.Self, T.OneOrManyFoo], T.OneOrManyBar ]:
    @wraps(func)
    def decorator(self: T.Self, arg: T.OneOrManyFoo) -> T.OneOrManyBar:
        if isinstance(arg, list):
            return [func(self, item) for item in arg]
        else:
            return func(self, arg)
    return decorator
