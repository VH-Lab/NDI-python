import pytest
from ndi import Session, Document

class MockDaqSystem:
    session_id = ''
    def __init__(self, id_):
        self.id = id_ or 'mock-daq-sys-id'

@pytest.fixture
def new_experiment():
    name = 'abc'
    daq_system_ids = ['1', '2', '3']
    daq_systems = [MockDaqSystem(id_=id_) for id_ in daq_system_ids]
    directory = './tests/data/intracell_example'
    e = Session(name, directory)
    yield e, name, directory, daq_system_ids

class TestSessionDocument:
    def test_new_experiment(self, new_experiment):
        """ndi.Session.__init__"""
        e, name, directory, ds_ids = new_experiment

        # metadata is properly set in document
        assert e.document.data['_metadata']['name'] == name
        assert e.document.data['_metadata']['type'] == Session.DOCUMENT_TYPE
        assert e.document.data['_metadata']['session_id'] == e.id

    def test_document_to_experiment(self, new_experiment):
        """ndi.Session.from_document"""
        e, name, directory, ds_ids = new_experiment

        d = e.document
        rebuilt_experiment = Session.from_document(d)
        assert rebuilt_experiment == e
