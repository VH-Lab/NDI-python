from abc import ABC, abstractmethod
import flatbuffers
from uuid import uuid4


class NDI_Object(ABC):
    @abstractmethod
    def __init__(self, id_):
        self.id = id_ or uuid4().hex

    # Flatbuffer Methods for converting to and from flatbuffers
    @classmethod
    @abstractmethod
    def frombuffer(cls, buffer):
        """
        Creates ndi_object instance from flatbuffer

            ndi_object = GetRootAsNDIObject(buffer, 0)

            return cls._reconstruct(ndi_object)
        """
        pass

    @classmethod
    @abstractmethod
    def _reconstruct(cls, ndi_object):
        """
        Creates ndi_object instance from flatbuffer object 

            return cls(property=ndi_object.Property())
        """
        pass

    @classmethod
    def _reconstructList(cls, ndi_object_parent):
        """
        Creates ndi_object instances for flatbuffer objects in a vector 
        """
        return [
            cls._reconstruct(getattr(ndi_object_parent, f'{cls.__name__}s')(i))
            for i in range(getattr(ndi_object_parent, f'{cls.__name__}sLength')())
        ]

    @abstractmethod
    def _build(self, builder):
        """
        Builds flatbuffer of object instance

            NDIObjectStart(builder)

            NDIObjectAddProperty(builder, property)

            return NDIObjectEnd(builder)
        """
        pass

    @staticmethod
    def _buildStringVector(builder, strings):
        """
        Builds flatbuffer vector from list of strings
        """
        built_strings = [
            builder.CreateString(string)
            for string in strings
        ]

        builder.StartVector(4, len(built_strings), 4)
        for built_string in reversed(built_strings):
            builder.PrependUOffsetTRelative(built_string)
        return builder.EndVector(len(built_strings))

    def serialize(self):
        """
        Returns flatbuffer of object instance
        """
        builder = flatbuffers.Builder(0)
        ndi_object = self._build(builder)
        builder.Finish(ndi_object)
        return builder.Output()

    def __eq__(self, ndi_object):
        return self.serialize() == ndi_object.serialize()
