import uuid
import abc

class Ido(abc.ABC):
    def __init__(self):
        self._id = str(uuid.uuid4())

    def id(self):
        return self._id
