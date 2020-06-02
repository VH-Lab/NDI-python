import pytest
from ndi import Experiment, Document, FileNavigator, Channel
from alchemy_mock.mocking import UnifiedAlchemyMagicMock
from ndi.database import SQL

def fix_get(Session):
    mock_get = Session.boundary['get']
    def get(db_items, id_):
        for item in db_items:
            if id_ == item.id:
                return item
    Session.boundary['get'] = get
    return Session

def add_delete_tracker(Session):
    Session.delete_tracker = []
    def delete(self, document):
        print('SESSION DELETE')
        self.Session.delete_tracker.append(document)
    Session.delete = delete
    return Session

@pytest.fixture
def new_sql_db():
    Session = fix_get(add_delete_tracker(UnifiedAlchemyMagicMock()))
    db = SQL('nonexistant_db', mock_session=Session)
    yield db

class MockBinaryCollection: pass
class MockDaqReader: pass
class MockDaqSystem:
    def __init__(self, id_):
        self.id = id_
        self.document = Document({}, 'daqsys')
        self.metadata = {}
        self.daq_reader = MockDaqReader
        self.file_navigator = FileNavigator('*', '*')

@pytest.fixture
def new_experiment():
    e = Experiment('test_experiment')
    yield e

class TestExperimentDocument:
    def test_overwrite_with_document(self, new_experiment):
        """ndi.core.Experiment.__overwrite_with_document()"""
        e = new_experiment
        d = Document({'words': 'lalala'}, 'new doc')
        
        # the method overwrites the document object on experiment
        assert d != e.document
        e._Experiment__overwrite_with_document(d)
        assert d == e.document

    def test_connect(self, new_experiment, new_sql_db):
        """ndi.core.Experiment.connect()"""
        e = new_experiment
        directory = 'test_dir'
        db = new_sql_db
        ds = MockDaqSystem('daqsysid')
        e.connect(
            directory=directory,
            database=db,
            binary_collection=MockBinaryCollection,
            daq_systems=[ds]
        )
        # all auxillary systems are set in experiment
        assert e.directory == directory
        assert e.ctx == db
        assert e.binary_collection == MockBinaryCollection
        assert e.daq_systems[0] == ds
        assert e.daq_readers_map[MockDaqReader.__name__] == MockDaqReader
    
    def test_add_daq_system(self, new_experiment, new_sql_db):
        """ndi.core.Experiment.add_daq_system()"""
        e = new_experiment.connect(database=new_sql_db)
        dss = [
            MockDaqSystem('0'),
            MockDaqSystem('1'),
        ]
        for ds in dss:
            e.add_daq_system(ds)

        # live daq systems are added to experiment and set with experiment_id
        assert dss[0] in e.daq_systems
        assert dss[0].metadata['experiment_id'] == e.id
        assert dss[1] in e.daq_systems
        assert dss[1].metadata['experiment_id'] == e.id

    def test_add_related_obj_to_db(self, new_experiment, new_sql_db):
        """ndi.core.Experiment.add_related_obj_to_db()"""
        db = new_sql_db
        e = new_experiment.connect(
            database=db,
            binary_collection=MockDaqSystem
        )
        fn = FileNavigator('', '')
        e.add_related_obj_to_db(fn)

        # ndi.NDI_Object is set with experiment_id
        assert fn.metadata['experiment_id'] == e.id
        #   and with db and binary collection
        assert fn.ctx == db
        assert fn.binary_collection == e.binary_collection

    def test_set_readers(self, new_experiment, new_sql_db):
        """ndi.core.Experiment.set_readers()"""
        ds = MockDaqSystem('0')
        e = new_experiment.connect(
            database=new_sql_db,
            daq_systems=[ds]
        )
        channels = [
            Channel('0', 0, '', '', daq_reader_class_name=MockDaqReader.__name__),
            Channel('1', 1, '', '', daq_reader_class_name=MockDaqReader.__name__),
        ]
        e.set_readers(channels)

        # channel daq_readers are set by daq_reader_class_name
        for c in channels:
            assert c.daq_reader == ds.daq_reader

    def test_add_document(self, new_experiment, new_sql_db):
        """ndi.core.Experiment.add_related_obj_to_db()"""
        db = new_sql_db
        e = new_experiment.connect(
            database=db,
            binary_collection=MockDaqSystem
        )
        d = Document({}, 'testdoc')
        e.add_document(d)

        # ndi.Document is set with experiment_id
        assert d.metadata['experiment_id'] == e.id
        #   and with db and binary collection
        assert d.ctx == db
        assert d.binary_collection == e.binary_collection
