import pytest
from ndi import DaqSystem, Document

class MockDaqReader:
    def __init__(self, id_):
        self.id = id_ or 'mock-daq-reader-id'
class MockFileNavigator:
    def __init__(self, id_):
        self.id = id_ or 'mock-file-nav-id'

class MockEpochProbeMap:
    pass

@pytest.fixture
def new_daq_system():
    name = 'abc'
    session_id = '1234567890'
    fn_id = '0987654321'
    epoch_ids = ['123', '456']
    fn = MockFileNavigator(fn_id)

    # Instantiating DaqSystem object
    ds = DaqSystem(name, file_navigator=fn, daq_reader=MockDaqReader, session_id=session_id, epoch_probe_map=MockEpochProbeMap, epoch_ids=epoch_ids)
    yield ds, name, session_id, fn_id, epoch_ids

class TestDaqSystemDocument:
    def test_new_daq_system(self, new_daq_system):
        """ndi.DaqSystem.__init__"""
        ds, name, session_id, fn_id, epoch_ids = new_daq_system

        # metadata is properly set in document
        assert ds.document.data['_metadata']['name'] == name
        assert ds.document.data['_metadata']['type'] == DaqSystem.DOCUMENT_TYPE
        assert ds.document.data['_metadata']['session_id'] == session_id
        assert ds.document.data['epoch_ids'] == epoch_ids

    def test_document_to_daq_system(self, new_daq_system):
        """ndi.DaqSystem.from_document"""
        ds, name, session_id, fn_id, epoch_ids = new_daq_system

        d = ds.document
        rebuilt_daq_system = DaqSystem.from_document(d)
        # Test that rebuilt DaqSystem properties match the original's
        assert rebuilt_daq_system.id == ds.id
        assert rebuilt_daq_system.base['name'] == ds.base['name']
        assert rebuilt_daq_system.metadata['session_id'] == ds.metadata['session_id']
        assert ds.document.data['epoch_ids'] == epoch_ids
