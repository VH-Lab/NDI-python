from .reader import Reader
from ...time.clocktype import ClockType

class Mfdaq(Reader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def epoch_clock(self, epochfiles):
        return [ClockType('dev_local_time')]

    def t0_t1(self, epochfiles):
        return [[float('nan'), float('nan')]]

    def get_channels_epoch(self, epochfiles):
        return []

    def get_channels_epoch_ingested(self, epochfiles, s):
        pass

    def read_channels_epoch_samples(self, channeltype, channel, epochfiles, s0, s1):
        pass

    def read_channels_epoch_samples_ingested(self, channeltype, channel, epochfiles, s0, s1, s):
        pass

    def read_events_epoch_samples(self, channeltype, channel, epochfiles, t0, t1):
        pass

    def read_events_epoch_samples_ingested(self, channeltype, channel, epochfiles, t0, t1, s):
        pass

    def read_events_epoch_samples_native(self, channeltype, channel, epochfiles, t0, t1):
        pass

    def samplerate(self, epochfiles, channeltype, channel):
        pass

    def samplerate_ingested(self, epochfiles, channeltype, channel, s):
        pass

    def underlying_datatype(self, epochfiles, channeltype, channel):
        pass

    def ingest_epoch_files(self, epochfiles, epoch_id):
        pass

    @staticmethod
    def channel_types():
        types =  ['analog_in','analog_out','auxiliary_in','digital_in','digital_out','event','marker','text','time']
        abbrev = ['ai', 'ao', 'ax', 'di', 'do', 'e', 'mk', 'tx', 't']
        return types, abbrev

    @staticmethod
    def standardize_channel_types(channeltypes):
        stdchanneltypes = channeltypes[:]
        types, abbrev = Mfdaq.channel_types()
        for i, channeltype in enumerate(channeltypes):
            try:
                index = abbrev.index(channeltype)
                stdchanneltypes[i] = types[index]
            except ValueError:
                pass # it's not an abbreviation
        return stdchanneltypes

    @staticmethod
    def channelsepoch2timechannelinfo(channelsepoch, channeltype, channelnumber):
        pass
