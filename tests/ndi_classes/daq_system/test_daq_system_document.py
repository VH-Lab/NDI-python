import pytest
from ndi import DaqSystem, Document

class MockDaqReader:
    def __init__(self, id_):
        self.id = id_ or 'mock-daq-reader-id'
class MockFileNavigator:
    def __init__(self, id_):
        self.id = id_ or 'mock-file-nav-id'

@pytest.fixture
def new_daq_system():
    name = 'abc'
    experiment_id = '1234567890'
    fn_id = '0987654321'
    fn = MockFileNavigator(fn_id)
    ds = DaqSystem(name, file_navigator=fn, daq_reader=MockDaqReader, experiment_id=experiment_id)
    yield ds, name, experiment_id, fn_id

class TestDaqSystemDocument:
    def test_new_daq_system(self, new_daq_system):
        """ndi.DaqSystem.__init__"""
        ds, name, experiment_id, fn_id = new_daq_system

        # metadata is properly set in document
        assert ds.document.data['_metadata']['name'] == name
        assert ds.document.data['_metadata']['type'] == DaqSystem.DOCUMENT_TYPE
        assert ds.document.data['_metadata']['experiment_id'] == experiment_id

    def test_document_to_daq_system(self, new_daq_system):
        """ndi.DaqSystem.from_document"""
        ds, name, experiment_id, fn_id = new_daq_system

        d = ds.document
        rebuilt_daq_system = DaqSystem.from_document(d)
        assert rebuilt_daq_system.id == ds.id
        assert rebuilt_daq_system.metadata['name'] == ds.metadata['name']
        assert rebuilt_daq_system.metadata['experiment_id'] == ds.metadata['experiment_id']
