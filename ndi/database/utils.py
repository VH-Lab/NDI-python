"""
Database Utils Module
*********************
"""
from ..ndi_object import NDI_Object
from functools import wraps
from contextlib import contextmanager
from ndi.database.query import Query


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
    """.. currentmodule:: ndi.database.sql
    
    Decorator: meant to work with :class:`SQL` methods. Ensures that the first argument passed into the decorated function is a list. If the value is not a list, it is wrapped in one.
    
    :param func:
    :type func: function
    :return: Returns return value of decorated function.
    """
    @wraps(func)
    def decorator(self, arg, *args, **kwargs):
        if not isinstance(arg, list):
            func(self, [arg], *args, **kwargs)
        else:
            func(self, arg, *args, **kwargs)
    return decorator

def check_ndi_objects(func):
    """Decorator: meant to work with :class:`SQL` methods. Ensures that every item in the first argument is a valid :term:`NDI object`.
    
    :param func:
    :type func: function
    :return: Returns return value of decorated function.
    """
    @wraps(func)
    def decorator(self, ndi_objects, *args, **kwargs):
        if len(ndi_objects):
            for item in ndi_objects:
                if not isinstance(item, NDI_Object):
                    raise TypeError(f'\'{item}\' is not an instance of an \'NDI_Object\' child class.')
            func(self, ndi_objects, *args, **kwargs)
    return decorator

def update_flatbuffer(ndi_class, flatbuffer, payload):
    """Decorator: meant to work with :class:`Collection` methods. Converts a list of :term:`NDI object`\ s into their :term:`SQLA document` equivalents.
    
    :param func:
    :type func: function
    :return: Returns return value of decorated function.
    """
    ndi_object = ndi_class.from_flatbuffer(flatbuffer)
    for key, value in payload.items():
        setattr(ndi_object, key, value)
    return ndi_object.serialize()

def print_everything_in(db):
    for collection in db._collections:
        results = db.find(collection)
        print(collection.__name__ + 's')
        for doc in results:
            try: print(f'  - {doc.name}')
            except AttributeError: print(f'  - {doc.id}')
        if results:
            print('  ---NONE---')
        print('')

def destroy_everything_in(db):
    for collection in db._collections:
        db.delete_many(collection)




"""
SQL Database Specific
=====================
"""

def recast_ndi_objects_to_documents(func):
    """Decorator: meant to work with :class:`Collection` methods. Converts a list of :term:`NDI object`\ s into their :term:`SQLA document` equivalents.
    
    :param func:
    :type func: function
    :return: Returns return value of decorated function.
    """
    @wraps(func)
    def decorator(self, ndi_objects, *args, **kwargs):
        items = [ self.create_document_from_ndi_object(o) for o in ndi_objects ]
        return func(self, items, *args, **kwargs)
    return decorator

def translate_query(func):
    """Decorator: meant to work with :class:`Collection` methods. Converts an :term:`NDI query` into an equivalent :term:`SQLA query`.
    
    :param func:
    :type func: function
    :return: Returns return value of decorated function.
    """
    @wraps(func)
    def decorator(self, *args, query=None, sqla_query=None, **kwargs):
        if isinstance(query, Query):
            query = self.generate_sqla_filter(query)
        elif query is None:
            if sqla_query is not None:
                query = sqla_query
            else: pass
        else:
            raise TypeError(f'{query} must be of type Query or CompositeQuery.')
        return func(self, *args, query=query, **kwargs)
    return decorator

def with_session(func):
    """Handle session instantiation, commit, and close operations for a class method. Passes session as first argument into decorated func.
    
    :param func:
    :type func: function
    :return: Returns return value of decorated function.
    """
    @wraps(func)
    def decorator(self, *args, session=None, **kwargs):
        enclosed_session = session is None
        if enclosed_session: 
            session = self.Session()
        output = func(self, session, *args, **kwargs)
        if enclosed_session:
            session.commit()
            session.close()
        return output
    return decorator

def with_open_session(func):
    """Handle session setup/teardown as a context manager for a class method. Returns decorated func for use as a context manager with session as its first argument.
    
    :param func:
    :type func: function
    :return: Returns return value of decorated function.
    """
    @wraps(func)
    @contextmanager
    def decorator(self, *args, session=None, **kwargs):
        enclosed_session = session is None
        if enclosed_session:
            session = self.Session()
        yield func(self, session, *args, **kwargs)
        if enclosed_session:
            session.commit()
            session.close()
    return decorator