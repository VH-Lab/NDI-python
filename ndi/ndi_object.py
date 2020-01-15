from abc import ABC, abstractmethod
import flatbuffers

class NDI_Object(ABC):
    @abstractmethod
    def __init__(self):
        pass

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
    def _buildVector(builder, ndi_objects):
        """
        Builds flatbuffer vectors of ndi_object
        """
        built_ndi_objects = [
            ndi_object._build(builder)
            for ndi_object in ndi_objects
        ]
        
        builder.StartVector(4, len(built_ndi_objects), 4)
        for built_ndi_object in reversed(built_ndi_objects):
            builder.PrependUOffsetTRelative(built_ndi_object)
        return builder.EndVector(len(built_ndi_objects))

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
