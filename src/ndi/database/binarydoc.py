import abc

class BinaryDoc(abc.ABC):
    """
    An abstract class for reading and writing binary data.
    """

    @abc.abstractmethod
    def fopen(self):
        raise NotImplementedError

    @abc.abstractmethod
    def fseek(self, location, reference):
        raise NotImplementedError

    @abc.abstractmethod
    def ftell(self):
        raise NotImplementedError

    @abc.abstractmethod
    def feof(self):
        raise NotImplementedError

    @abc.abstractmethod
    def fwrite(self, data, precision, skip):
        raise NotImplementedError

    @abc.abstractmethod
    def fread(self, count, precision, skip):
        raise NotImplementedError

    @abc.abstractmethod
    def fclose(self):
        raise NotImplementedError
