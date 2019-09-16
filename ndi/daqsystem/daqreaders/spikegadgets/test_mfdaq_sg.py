from ndi.daqsystem.mfdaq import DaqSystemMultiFunction
from ndi.daqsystem.daqreaders.spikegadgets.mfdaq_sg import DaqReaderMultiFunctionSg


def test_read_req():
    reader = DaqReaderMultiFunctionSg('tests/data/daqreaders/spikegadgets/CS31_20170201_OdorPlace1short.rec')
    daq_system = DaqSystemMultiFunction('test_daq', reader)

    assert daq_system
