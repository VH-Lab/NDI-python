from ndi.epochprobemap.vhintan_channelgrouping import vh_intan_channel_grouping, read_device_string
import pytest


class TestEpochProbeMap:
    @pytest.mark.parametrize(
        'device_string, expected_output',
        [
            (
                'mySpike2:ai3-5,7,9-11',
                {
                    'device_name': 'mySpike2',
                    'channel_type': 'analog_in',
                    'channel_list': [3, 4, 5, 7, 9, 10, 11]
                }
            ),
            (
                'dev1:e22,24,30-33',
                {
                    'device_name': 'dev1',
                    'channel_type': 'event',
                    'channel_list': [22, 24, 30, 31, 32, 33]
                }
            ),
            (
                'name:t3-4,6,8-10',
                {
                    'device_name': 'name',
                    'channel_type': 'time',
                    'channel_list': [3, 4, 6, 8, 9, 10]
                }
            )
        ]
    )
    def test_read_device_string(self, device_string, expected_output):
        assert read_device_string(device_string) == expected_output

    @pytest.mark.parametrize(
        'epochprobemap, expected_output',
        [
            (
                './tests/data/epochprobemaps/example1.epochmetadata',
                [
                    {
                        'name': 'intra',
                        'reference': 1,
                        'type': 'sharp-Vm',
                        'devicestring': {
                            'device_name': 'mySpike2',
                            'channel_type': 'analog_in',
                            'channel_list': [21]
                        },
                        'subjectstring': 'anteater37@nosuchlab.org'
                    },
                    {
                        'name': 'pro',
                        'reference': 2,
                        'type': 'intranode',
                        'devicestring': {
                            'device_name': 'mySpike2',
                            'channel_type': 'event',
                            'channel_list': [22, 23, 24, 26]
                        },
                        'subjectstring': 'mouse43@mylab.org'}
                    ]
            )
        ]
    )
    def test_vh_intan_channel_grouping(self, epochprobemap, expected_output):
        assert vh_intan_channel_grouping(epochprobemap) == expected_output
