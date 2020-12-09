import pytest
from ndi import Epoch, Document

@pytest.fixture
def new_epoch():
    session_id = '1234567890'
    e = Epoch(session_id=session_id)
    yield e, session_id

class TestEpochDocument:
    def test_new_epoch(self, new_epoch):
        """ndi.Epoch.__init__"""
        e, session_id = new_epoch

        # metadata is properly set in document
        assert e.document.class_['name'] == Epoch.DOCUMENT_TYPE
        assert e.document.base['session_id'] == session_id

    def test_document_to_epoch(self, new_epoch):
        """ndi.Epoch.from_document"""
        e, session_id = new_epoch

        d = e.document
        rebuilt_epoch = Epoch.from_document(d)
        assert rebuilt_epoch == e
