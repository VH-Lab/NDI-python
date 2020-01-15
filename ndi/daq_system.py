from ndi import NDI_Object, Probe
import ndi.build.DaqSystem as build_daq_system


class DaqSystem(NDI_Object):
    def __init__(self, name, probes):
        self.name = name
        self.probes = probes

    @classmethod
    def frombuffer(cls, buffer):
        daq_system = build_daq_system.DaqSystem.GetRootAsDaqSystem(buffer, 0)
        return cls._reconstruct(daq_system)

    @classmethod
    def _reconstruct(cls, daq_system):
        probes = Probe._reconstructList(daq_system)
        return cls(name=daq_system.Name().decode('utf8'),
                   probes=probes)

    def _build(self, builder):
        name = builder.CreateString(self.name)
        probes = self._buildVector(builder, self.probes)

        build_daq_system.DaqSystemStart(builder)
        build_daq_system.DaqSystemAddName(builder, name)
        build_daq_system.DaqSystemAddProbes(builder, probes)
        return build_daq_system.DaqSystemEnd(builder)
