from ndi.daqreaders.cedspike2 import CEDSpike2


class TestCEDSpike2:
    def test_samplerate(self):
        daq_reader = CEDSpike2('./tests/data/daqreaders/cedspike2/example1.smr')
        channel_number = 21
        expected_samplerate = 1/.00009
        assert daq_reader.samplerate(channel_number) == expected_samplerate

        daq_reader = CEDSpike2('./tests/data/daqreaders/cedspike2/example2.smr')
        channel_number = 21
        expected_samplerate = 1/.00009
        assert daq_reader.samplerate(channel_number) == expected_samplerate

        daq_reader = CEDSpike2('./tests/data/daqreaders/cedspike2/example3.smr')
        channel_number = 21
        expected_samplerate = 1/.00009
        assert daq_reader.samplerate(channel_number) == expected_samplerate
