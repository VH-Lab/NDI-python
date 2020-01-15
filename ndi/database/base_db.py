from abc import ABC, abstractmethod

class BaseDB(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add_experiment(self):
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
