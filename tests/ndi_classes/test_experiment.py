import pytest
from ndi import Session, Document

class MockDaqSystem:
    session_id = ''
    def __init__(self, id_):
        self.id = id_ or 'mock-daq-sys-id'

@pytest.fixture
def new_session():
    name = 'abc'
    daq_system_ids = ['1', '2', '3']
    daq_systems = [MockDaqSystem(id_=id_) for id_ in daq_system_ids]
    directory = './tests/data/intracell_example'
    e = Session(name, directory)
    yield e, name, directory, daq_system_ids

class TestSessionDocument:
    def test_new_session(self, new_session):
        """ndi.Session.__init__"""
        e, name, directory, ds_ids = new_session

        # metadata is properly set in document
        assert e.document.data['_metadata']['name'] == name
        assert e.document.data['_metadata']['type'] == Session.DOCUMENT_TYPE
        assert e.document.data['_metadata']['session_id'] == e.id

    def test_document_to_session(self, new_session):
        """ndi.Session.from_document"""
        e, name, directory, ds_ids = new_session

        d = e.document
        rebuilt_session = Session.from_document(d)
        assert rebuilt_session == e
