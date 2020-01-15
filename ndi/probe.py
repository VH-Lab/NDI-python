from ndi import NDI_Object, Channel
import ndi.build.Probe as build_probe
from ndi.build.ProbeType import ProbeType as build_probe_type
from .probe_type import ProbeType
from .probe_file_types import wav


class Probe(NDI_Object):
    def __init__(self, name, probe_type, channels):
        self.name = name
        self.probe_type = ProbeType[probe_type]
        self.probe_type_key = probe_type
        self.channels = channels

    # Flatbuffer-Interface Methods
    @classmethod
    def frombuffer(cls, buffer):
        probe = build_probe.Probe.GetRootAsProbe(buffer, 0)
        return cls._reconstruct(probe)

    @classmethod
    def _reconstruct(cls, probe):
        channels = Channel._reconstructList(probe)
        return cls(name=probe.Name().decode('utf8'),
                   probe_type=probe.ProbeType(),
                   channels=channels)

    def _build(self, builder):
        name = builder.CreateString(self.name)
        channels = self._buildVector(builder, self.channels)

        build_probe.ProbeStart(builder)
        build_probe.ProbeAddName(builder, name)
        build_probe.ProbeAddProbeType(builder, self.probe_type_key)
        build_probe.ProbeAddChannels(builder, channels)
        return build_probe.ProbeEnd(builder)

    # Probe File Type Class Methods:
    @classmethod
    def fromwavfile(cls, name, probe_type, path):
        return cls(name=name,
                   probe_type=probe_type,
                   channels=wav.getChannels(path))
