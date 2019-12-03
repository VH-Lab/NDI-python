from abc import ABC, abstractmethod

class AbstractDatabase(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def add(self):
        pass

    @abstractmethod
    def find(self):
        pass
