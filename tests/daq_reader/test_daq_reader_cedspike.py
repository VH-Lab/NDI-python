from ndi.daqreaders.cedspike2 import CEDSpike2

class TestCEDSpike2:
    def test_samplerate(self):
        daq_reader = CEDSpike2('./tests/data/daqreaders/cedspike2/example1.smr')
        assert daq_reader.samplerate(21) == 11111.1111
