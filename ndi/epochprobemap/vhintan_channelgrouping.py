from uuid import uuid4
import re


def vh_intan_channel_grouping(file_path):
    probes = []
    with open(file_path) as file:
        keys = [key.strip() for key in file.readline().split('\t')]
        for probe_mapping in file.readlines():
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
