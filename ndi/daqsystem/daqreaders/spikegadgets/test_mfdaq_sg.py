from ndi.daqsystem.daqreaders.spikegadgets.mfdaq_sg import DaqReaderMultiFunctionSg


def test_read_req():
    daq = DaqReaderMultiFunctionSg(
        'tests/data/daqreaders/spikegadgets/CS31_20170201_OdorPlace1short.rec')

    assert daq
