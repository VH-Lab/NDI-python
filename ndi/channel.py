from ndi import NDI_Object
import ndi.build.Channel as build_channel
from .channel_type import ChannelType


class Channel(NDI_Object):
    def __init__(self, number, channel_type, data):
        self.number = number
        self.channel_type = ChannelType[channel_type]
        self.channel_type_key = channel_type
        self.data = data

    @classmethod
    def frombuffer(cls, buffer):
        channel = build_channel.Channel.GetRootAsChannel(buffer, 0)
        return cls._reconstruct(channel)

    @classmethod
    def _reconstruct(cls, channel):
        return cls(number=channel.Number(),
                   channel_type=channel.ChannelType(),
                   data=channel.DataAsNumpy())

    def _build(self, builder):
        data = builder.CreateNumpyVector(self.data)
        
        build_channel.ChannelStart(builder)
        build_channel.ChannelAddNumber(builder, self.number)
        build_channel.ChannelAddChannelType(builder, self.channel_type_key)
        build_channel.ChannelAddData(builder, data)
        return build_channel.ChannelEnd(builder)
