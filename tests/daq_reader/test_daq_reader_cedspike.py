from ndi.daqreaders.cedspike2 import CEDSpike2
import pytest


class TestCEDSpike2:
    @pytest.mark.parametrize(
        'test_file, channel_number, expected_samplerate',
        [
            ('./tests/data/daqreaders/cedspike2/example1.smr', 21, 1 / .00009),
            ('./tests/data/daqreaders/cedspike2/example2.smr', 21, 1 / .00009),
            ('./tests/data/daqreaders/cedspike2/example3.smr', 21, 1 / .00009),
            ('./tests/data/daqreaders/cedspike2/DemoData.smr', 1, 1 / .005),
            ('./tests/data/daqreaders/cedspike2/DemoData.smr', 2, 1 / .004),
            ('./tests/data/daqreaders/cedspike2/DemoData.smr', 3, 1 / .01),
        ]
    )
    def test_samplerate(self, test_file, channel_number, expected_samplerate):
        daq_reader = CEDSpike2(test_file)
        assert daq_reader.samplerate(channel_number) == expected_samplerate

    @pytest.mark.parametrize(
        'test_file, channel_number,  start_index, end_index, expected_length, expected_values_slice',
        [
            ('./tests/data/daqreaders/cedspike2/example1.smr', 21, 0, None, 5569702, [-0.9647, -0.9592, -0.9644, -0.9601, -0.9644]),
            ('./tests/data/daqreaders/cedspike2/example2.smr', 21, 500, 505, 5, [-0.7330, -0.7352, -0.7346, -0.7318, -0.7352]),
            ('./tests/data/daqreaders/cedspike2/example3.smr', 21, 1234, 2345, 1111, [-0.8685, -0.8685, -0.8640, -0.8728, -0.8621]),
            ('./tests/data/daqreaders/cedspike2/DemoData.smr', 1, 86, 101, 15, [-0.0391, -0.0391, 0.1927, 0.5370, 0.9959]),
            ('./tests/data/daqreaders/cedspike2/DemoData.smr', 2, 44, 57, 13, [112.7167, 116.3635, 110.0616, 105.4535, 105.4993]),
            ('./tests/data/daqreaders/cedspike2/DemoData.smr', 3, 42, 84, 42, [0.1591, 0.2080, 0.2129, 0.2226, 0.2422]),
        ]
    )
    def test_readchannel(self, test_file, channel_number, start_index, end_index, expected_length, expected_values_slice):
        daq_reader = CEDSpike2(test_file)
        data = daq_reader.readchannel(channel_number, start_index, end_index)
        assert len(data) == expected_length
        for i, item in enumerate(expected_values_slice):
            assert item == round(float(data[i]), 4)
