from .ndi_object import NDI_Object
import ndi.schema.Channel as build_channel
from ndi.schema.ClockType import ClockType as build_clock_type
from ndi.schema.ChannelType import ChannelType as build_channel_type
from .channel_type import ChannelType
from .clock_type import ClockType


class Channel(NDI_Object):
    """Channel
    
    :param NDI_Object: NDI Abstract Class
    :type NDI_Object: ABC
    :return: Channel instance
    :rtype: object
    """
    def __init__(self, name, number, type_, source_file, epoch_id, probe_id, daq_system_id, id_=None, clock_type='no_time',):
        super().__init__(id_)
        self.name = name
        self.number = number
        self.type = type_
        self.clock_type = clock_type
        self.source_file = source_file
        self.epoch_id = epoch_id
        self.probe_id = probe_id
        self.daq_system_id = daq_system_id

    @classmethod
    def frombuffer(cls, buffer):
        channel = build_channel.Channel.GetRootAsChannel(buffer, 0)
        return cls._reconstruct(channel)

    @classmethod
    def _reconstruct(cls, channel):
        return cls(id_=channel.Id().decode('utf8'),
                   name=channel.Name().decode('utf8'),
                   number=channel.Number(),
                   type_=ChannelType[channel.ChannelType()],
                   clock_type=ClockType[channel.ClockType()],
                   source_file=channel.SourceFile().decode('utf8'),
                   epoch_id=channel.EpochId().decode('utf8'),
                   probe_id=channel.ProbeId().decode('utf8'),
                   daq_system_id=channel.DaqSystemId().decode('utf8'))

    def _build(self, builder):
        id_ = builder.CreateString(self.id)
        name = builder.CreateString(self.name)
        source_file = builder.CreateString(self.source_file)
        epoch_id = builder.CreateString(self.epoch_id)
        probe_id = builder.CreateString(self.probe_id)
        daq_system_id = builder.CreateString(self.daq_system_id)

        build_channel.ChannelStart(builder)
        build_channel.ChannelAddId(builder, id_)
        build_channel.ChannelAddName(builder, name)
        build_channel.ChannelAddNumber(builder, self.number)
        build_channel.ChannelAddType(
            builder, getattr(build_channel_type, self.type))
        build_channel.ChannelAddClockType(
            builder, getattr(build_clock_type, self.clock_type))
        build_channel.ChannelAddSourceFile(builder, source_file)
        build_channel.ChannelAddEpochId(builder, epoch_id)
        build_channel.ChannelAddProbeId(builder, probe_id)
        build_channel.ChannelAddDaqSystemId(builder, daq_system_id)
        return build_channel.ChannelEnd(builder)
