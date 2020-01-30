from ..ndi_object import NDI_Object


def handle_iter(func):
    def decorator(self, arg):
        try:
            for item in arg:
                func(self, item)
        except:
            func(self, arg)
    return decorator


def check_ndi_object(func):
    @handle_iter
    def decorator(self, ndi_object):
        if isinstance(ndi_object, NDI_Object):
            return func(self, ndi_object)
        else:
            raise TypeError(f'\'{ndi_object}\' is not of type \'NDI_Object\'')
    return decorator
