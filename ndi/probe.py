from ndi import NDI_Object, Channel
import ndi.schema.Probe as build_probe
from ndi.schema.ProbeType import ProbeType as build_probe_type
from .probe_type import ProbeType


class Probe(NDI_Object):
    def __init__(self, name, reference, type_, id_=None, daq_system_id=None):
        super().__init__(id_)
        self.name = name
        self.type = type_
        self.daq_system_id = daq_system_id

    # Flatbuffer Methods
    @classmethod
    def frombuffer(cls, buffer):
        probe = build_probe.Probe.GetRootAsProbe(buffer, 0)
        return cls._reconstruct(probe)

    @classmethod
    def _reconstruct(cls, probe):
        return cls(id_=probe.Id().decode('utf8'),
                   name=probe.Name().decode('utf8'),
                   reference=probe.Reference(),
                   type_=ProbeType[probe.ProbeType()],
                   daq_system_id=probe.DaqSystemId().decode('utf8'))

    def _build(self, builder):
        id_ = builder.CreateString(self.id)
        name = builder.CreateString(self.name)
        daq_system_id = builder.CreateString(self.daq_system_id)

        build_probe.ProbeStart(builder)
        build_probe.ProbeAddId(builder, id_)
        build_probe.ProbeAddName(builder, name)
        build_probe.ProbeAddType(builder, getattr(build_probe_type, self.type))
        build_probe.ProbeAddDaqSystemId(builder, daq_system_id)
        return build_probe.ProbeEnd(builder)
