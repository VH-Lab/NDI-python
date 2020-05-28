import pytest
from ndi import Epoch, Document

@pytest.fixture
def new_epoch():
    daq_system_id = '0987654321'
    experiment_id = '1234567890'
    e = Epoch(daq_system_id=daq_system_id, experiment_id=experiment_id)
    yield e, daq_system_id, experiment_id

class TestEpochDocument:
    def test_new_epoch(self, new_epoch):
        """ndi.Epoch.__init__"""
        e, daq_system_id, experiment_id = new_epoch

        # metadata is properly set in document
        assert e.document.data['_metadata']['type'] == Epoch.DOCUMENT_TYPE
        assert e.document.data['_metadata']['experiment_id'] == experiment_id

        # data is properly set in document
        assert e.document.data['daq_system_id'] == daq_system_id

    def test_document_to_epoch(self, new_epoch):
        """ndi.Epoch.from_document"""
        e, daq_system_id, experiment_id = new_epoch

        d = e.document
        rebuilt_epoch = Epoch.from_document(d)
        assert rebuilt_epoch == e
