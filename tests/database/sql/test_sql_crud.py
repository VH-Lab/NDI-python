from ndi import Experiment, Document
from ndi import Document as NDIDocument
from did import DID, DIDDocument
from did.database import SQL
import pytest
import json

mock_document_data = [
    {
        'base': {
            'name': 'A',
            'datestamp': '2020-10-28T08:12:20+0000',
            'version': '1',
        },
        'depends_on': [],
        'document_class': {
            'definition': '$NDIDOCUMENTPATH\/ndi_document_app.json',
            'validation': '$NDISCHEMAPATH\/ndi_document_app_schema.json',
            'class_name': 'ndi_document_app',
            'property_list_name': 'app',
            'class_version': 1,
            'superclasses': [{
                'definition': '$NDIDOCUMENTPATH\/base_document.json'
            }],
        },
        'app': {
            'a': 'b',
            'c': 'd',
        },
    },
    {
        'base': {
            'name': 'B',
            'datestamp': '2020-10-28T08:12:20+0000',
            'version': '1',
        },
        'depends_on': ['0'],
        'document_class': {
            'definition': '$NDIDOCUMENTPATH\/ndi_document_app.json',
            'validation': '$NDISCHEMAPATH\/ndi_document_app_schema.json',
            'class_name': 'ndi_document_app',
            'property_list_name': 'app',
            'class_version': 1,
            'superclasses': [{
                'definition': '$NDIDOCUMENTPATH\/base_document.json'
            }],
        },
        'app': {
            'a': 'b',
            'c': 'd',
        },
    },
    {
        'base': {
            'name': 'C',
            'datestamp': '2020-10-28T08:12:20+0000',
            'version': '1',
        },
        'depends_on': [],
        'document_class': {
            'definition': '$NDIDOCUMENTPATH\/ndi_document_app.json',
            'validation': '$NDISCHEMAPATH\/ndi_document_app_schema.json',
            'class_name': 'ndi_document_app',
            'property_list_name': 'app',
            'class_version': 1,
            'superclasses': [{
                'definition': '$NDIDOCUMENTPATH\/base_document.json'
            }],
        },
        'app': {
            'a': 'b',
            'c': 'd',
        },
    },
]

@pytest.fixture
def experiment():
    did = DID(
        database = SQL(
            'postgres://postgres:password@localhost:5432/ndi_did_sql_tests', 
            {
                'hard_reset_on_init': True,
                'debug_mode': False,
            }
        ),
        binary_directory = './test_sql_crud'
    )
    yield Experiment('test_sql_crud').connect(
        data_interface_database = did,
    )

@pytest.fixture
def ndi_mocdocs():
    # names are 'A', 'B', and 'C'
    yield [NDIDocument(data) for data in mock_document_data]

def doc_count(db):
    return list(db.execute('select count(*) from document;'))[0][0]

def find_docs(db, where_clause = ''):
    return db.execute(f'select data from document {where_clause};')

class TestLookupCollection:
    def test_add_to_sql(self, experiment, ndi_mocdocs):
        experiment.add_document(ndi_mocdocs[0])
        response = list(find_docs(
            experiment.ctx.db.database.database,
            f'where document_id = \'{ndi_mocdocs[0].id}\''
        ))
        assert len(response) is 1
        data = json.loads(response[0][0])
        assert data['base']['session_id'] == experiment.id

    def test_add_duplicate_to_sql(self, experiment, ndi_mocdocs):
        db = experiment.ctx.db.database.database

        experiment.add_document(ndi_mocdocs[0])

        try:
            doc_count_before = doc_count(db)
            experiment.add_document(ndi_mocdocs[0])
            # if this call succeeds, test should fail
            assert False
        except RuntimeError as err:
            assert str(err) == 'Dependency key is already in use (dependency keys default to the document name if not specified).'
            doc_count_after = doc_count(db)
            assert doc_count_before == doc_count_after

    