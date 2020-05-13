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
