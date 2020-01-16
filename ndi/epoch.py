from .ndi_object import NDI_Object
import ndi.schema.Epoch as build_epoch


class Epoch(NDI_Object):
    def __init__(self, id_=None):
        super().__init__(id_)

    @classmethod
    def frombuffer(cls, buffer):
        epoch = build_epoch.Epoch.GetRootAsEpoch(buffer, 0)
        return cls._reconstruct(epoch)

    @classmethod
    def _reconstruct(cls, epoch):
        return cls(id_=epoch.Id().decode('utf8'))

    def _build(self, builder):
        id_ = builder.CreateString(self.id)

        build_epoch.EpochStart(builder)
        build_epoch.EpochAddId(builder, id_)
        return build_epoch.EpochEnd(builder)
