import re
from .epoch_probe_map import EpochProbeMap
from ..epoch import Epoch
from ..probe import Probe
from ..channel import Channel


class VHIntanChannelGrouping(EpochProbeMap):
    def __init__(self, daq_reader, epoch_sets, daq_system_id, experiment_id):
        self.daq_reader = daq_reader
        self.epoch_sets = epoch_sets
        self.daq_system_id = daq_system_id
        self.experiment_id = experiment_id

    def read_epoch_metadata_file(self, metadata_file_path):
        probes = []
        with open(metadata_file_path) as metadata_file:
            keys = [key.strip() for key in metadata_file.readline().split('\t')]
            for probe_mapping in metadata_file.readlines():
                values = [value.strip() for value in probe_mapping.split('\t')]
                probes.append({
                    key: value
                    for key, value
                    in zip(keys, values)
                })
        for probe in probes:
            probe['devicestring'] = read_device_string(probe['devicestring'])
            probe['reference'] = int(probe['reference'])
        return probes

    def get_epochs_probes_channels(self):
        epochs = [
            Epoch(experiment_id=self.experiment_id)
            for _ in range(len(self.epoch_sets))
        ]

        probes = []
        channels = []

        epoch_probe_maps = [
            self.read_epoch_metadata_file(epoch_set.metadatafile)
            for epoch_set in self.epoch_sets
        ]

        for epoch_probe_map, epoch, epoch_set in zip(epoch_probe_maps, epochs, self.epoch_sets):
            for probe_map in epoch_probe_map:
                if probe_map['reference'] not in [probe.reference for probe in probes]:
                    probes.append(
                        Probe(
                            name=probe_map['name'],
                            reference=probe_map['reference'],
                            type_=probe_map['type'],
                            daq_system_id=self.daq_system_id,
                            experiment_id=self.experiment_id
                        )
                    )

                current_probe = next(
                    probe
                    for probe in probes
                    if probe.reference == probe_map['reference']
                )

                source_file = next(
                    data_file
                    for data_file in epoch_set.epochfiles
                    if data_file.endswith(self.daq_reader.extensions)
                )

                for channel_number in probe_map['devicestring']['channel_list']:
                    channels.append(
                        Channel(
                            number=channel_number,
                            type_=probe_map['devicestring']['channel_type'],
                            source_file=source_file,
                            daq_reader=self.daq_reader,
                            epoch_id=epoch.id,
                            probe_id=current_probe.id,
                            daq_system_id=self.daq_system_id,
                            experiment_id=self.experiment_id
                        )
                    )
        
        return epochs, probes, channels


def read_device_string(device_string):
    device_name, channel_info = device_string.split(':')
    device_string_pattern = '(?P<channel_type>[a-zA-Z]+)(?P<channel_string>.*)'
    match = re.match(device_string_pattern, channel_info)
    channel_type = match.group('channel_type')
    channel_string = match.group('channel_string')

    channel_list = []
    for channel_group in channel_string.split(','):
        channels = [int(channel) for channel in channel_group.split('-')]
        if len(channels) == 1:
            channel_list.append(channels[0])
        else:
            for channel in range(channels[0], channels[1] + 1):
                channel_list.append(channel)

    return {
        'device_name': device_name,
        'channel_type': channeltypemap[channel_type],
        'channel_list': channel_list
    }


channeltypemap = {
    'ai': 'analog_in',
    'ao': 'analog_out',
    'di': 'digital_in',
    'do': 'digital_out',
    't': 'time',
    'ax': 'auxiliary',
    'mk': 'mark',
    'e': 'event'
}
