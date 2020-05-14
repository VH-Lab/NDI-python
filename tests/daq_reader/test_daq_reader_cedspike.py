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
    
    def test_readchannel(self):
        daq_reader = CEDSpike2('./tests/data/daqreaders/cedspike2/example1.smr')
        channel_number = 21
        start_time = 0
        # end_time value of -1 means read to the end of channel data
        end_time = -1
        data = daq_reader.readchannel(channel_number, start_time, end_time)
        expected_values_slice = [
            -0.9647,
            -0.9592,
            -0.9644,
            -0.9601,
            -0.9644,
            -0.9598,
            -0.9604,
            -0.9561,
            -0.9555,
            -0.9506
        ]
        for i, item in enumerate(expected_values_slice):
            assert item == data[i]
