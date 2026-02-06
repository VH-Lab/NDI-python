import abc

class NDIMeta(type):
    def __new__(cls, name, bases, dct):
        # Find the metaclass that is a subclass of ABCMeta
        meta = abc.ABCMeta
        for base in bases:
            if isinstance(base, abc.ABCMeta):
                meta = base
                break
        return meta(name, bases, dct)
