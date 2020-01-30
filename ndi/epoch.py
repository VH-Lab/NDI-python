from .ndi_object import NDI_Object
import ndi.schema.Epoch as build_epoch


class Epoch(NDI_Object):
    # TODO: require daq_system_id after implementing DaqReaders
    def __init__(self, daq_system_id='', id_=None):
        super().__init__(id_)
        self.daq_system_id = daq_system_id

    @classmethod
    def from_flatbuffer(cls, flatbuffer):
        epoch = build_epoch.Epoch.GetRootAsEpoch(flatbuffer, 0)
        return cls._reconstruct(epoch)

    @classmethod
    def _reconstruct(cls, epoch):
        return cls(id_=epoch.Id().decode('utf8'),
                   daq_system_id=epoch.DaqSystemId().decode('utf8'))

    def _build(self, builder):
        id_ = builder.CreateString(self.id)
        daq_system_id = builder.CreateString(self.daq_system_id)

        build_epoch.EpochStart(builder)
        build_epoch.EpochAddId(builder, id_)
        build_epoch.EpochAddDaqSystemId(builder, daq_system_id)
        return build_epoch.EpochEnd(builder)
