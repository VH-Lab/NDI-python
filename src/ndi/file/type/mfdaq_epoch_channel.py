from ....util.vlt import file as vlt_file
from ....fun.channel_name_to_prefix_number import channel_name_to_prefix_number

class MfdaqEpochChannel:
    def __init__(self, channel_structure=None, filename=None):
        self.channel_information = []
        if channel_structure is not None:
            self.create_properties(channel_structure)
        elif filename is not None:
            self.read_from_file(filename)

    def create_properties(self, channel_structure, **kwargs):
        # Default values
        params = {
            'analog_in_channels_per_group': 400,
            'analog_out_channels_per_group': 400,
            'auxiliary_in_channels_per_group': 400,
            'auxiliary_out_channels_per_group': 400,
            'digital_in_channels_per_group': 512,
            'digital_out_channels_per_group': 512,
            'eventmarktext_channels_per_group': 100000,
            'time_channels_per_group': 100000,
            'analog_in_dataclass': 'ephys',
            'analog_out_dataclass': 'ephys',
            'auxiliary_in_dataclass': 'ephys',
            'auxiliary_out_dataclass': 'ephys',
            'digital_in_dataclass': 'digital',
            'digital_out_dataclass': 'digital',
            'eventmarktext_dataclass': 'eventmarktext',
            'time_dataclass': 'time',
        }
        params.update(kwargs)

        # Sort channels by type
        channel_structure.sort(key=lambda x: x['type'])

        self.channel_information = []
        types_available = sorted(list(set(c['type'] for c in channel_structure)))

        for channel_type in types_available:
            channels_here = [c for c in channel_structure if c['type'] == channel_type]
            channels_here.sort(key=lambda x: channel_name_to_prefix_number(x['name'])[1])

            channels_per_group = params[f"{channel_type}_channels_per_group"]
            dataclass = params[f"{channel_type}_dataclass"]

            for c in channels_here:
                _, number = channel_name_to_prefix_number(c['name'])
                group = 1 + (number // channels_per_group)
                self.channel_information.append({
                    'name': c['name'],
                    'type': c['type'],
                    'time_channel': c.get('time_channel'),
                    'sample_rate': c['sample_rate'],
                    'offset': c['offset'],
                    'scale': c['scale'],
                    'number': number,
                    'group': group,
                    'dataclass': dataclass,
                })

    def read_from_file(self, filename):
        self.channel_information = vlt_file.load_struct_array(filename)

    def write_to_file(self, filename):
        try:
            vlt_file.save_struct_array(filename, self.channel_information)
            return True, ""
        except Exception as e:
            return False, str(e)

    @staticmethod
    def channel_group_decoding(channel_info, channel_type, channels):
        groups = []
        channel_indexes_in_groups = {}
        channel_indexes_in_output = {}

        ci = [c for c in channel_info if c['type'] == channel_type]

        for i, channel_num in enumerate(channels):
            try:
                index = next(j for j, c in enumerate(ci) if c['number'] == channel_num)
                channel = ci[index]
                if channel['group'] not in groups:
                    groups.append(channel['group'])
                    channel_indexes_in_groups[channel['group']] = []
                    channel_indexes_in_output[channel['group']] = []

                subset_group = [c for c in ci if c['group'] == channel['group']]
                chan_index_in_group = next(j for j, c in enumerate(subset_group) if c['number'] == channel_num)

                channel_indexes_in_groups[channel['group']].append(chan_index_in_group)
                channel_indexes_in_output[channel['group']].append(i)
            except StopIteration:
                raise ValueError(f"Channel number {channel_num} not found in record.")

        # Convert dicts to lists of lists for the final output
        final_channel_indexes_in_groups = [channel_indexes_in_groups[g] for g in sorted(groups)]
        final_channel_indexes_in_output = [channel_indexes_in_output[g] for g in sorted(groups)]

        return sorted(groups), final_channel_indexes_in_groups, final_channel_indexes_in_output
