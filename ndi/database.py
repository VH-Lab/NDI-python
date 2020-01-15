from abc import ABC, abstractmethod
class Database(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def __delattr__(self, name):

