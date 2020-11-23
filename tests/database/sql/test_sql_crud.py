from ndi import Experiment, Document
from ndi import Document as NDIDocument
from did import DID, DIDDocument, Query as Q
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
            'a': True,
            'b': True,
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
            'a': True,
            'b': False,
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
            'a': False,
            'b': False,
        },
    },
]

@pytest.fixture
def experiment():
    did = DID(
        database = SQL(
            'postgres://postgres:password@localhost:5432/ndi_did_sql_tests', 
            hard_reset_on_init = True,
            debug_mode = False,
            verbose_feedback = False,
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

class TestSqlCrud:
    def test_add(self, experiment, ndi_mocdocs):
        experiment.add_document(ndi_mocdocs[0])
        response = list(find_docs(
            experiment.ctx.db.database.database,
            f'where document_id = \'{ndi_mocdocs[0].id}\''
        ))
        assert len(response) is 1
        data = response[0][0]
        assert data['base']['session_id'] == experiment.id

    def test_add_duplicate(self, experiment, ndi_mocdocs):
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

    def test_find_by_id(self, experiment, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            experiment.add_document(ndi_doc)
        
        # get_document_dependencies() makes calls to find_by_id
        document_dependencies = experiment.get_document_dependencies().items()
        assert len(ndi_mocdocs) == len(document_dependencies)
        for name, ndi_doc in document_dependencies:
            assert any([d.data['base']['name'] == name for d in ndi_mocdocs])

    def test_find(self, experiment, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            experiment.add_document(ndi_doc)
        
        by_app_a = Q('app.a') == True
        found_ids = [doc.id for doc in experiment.find_documents(by_app_a)]
        expected_ids = [doc.id for doc in ndi_mocdocs if doc.data['app']['a'] == True]
        assert found_ids == expected_ids

        by_app_a_and_name = by_app_a & (Q('base.name') == 'A')
        found_ids = [doc.id for doc in experiment.find_documents(by_app_a_and_name)]
        expected_ids = [
            doc.id for doc in ndi_mocdocs
            if doc.data['app']['a'] == True
            and doc.data['base']['name'] == 'A'
        ]
        assert found_ids == expected_ids

    def test_update(self, experiment, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            experiment.add_document(ndi_doc)

        docs_from_db = experiment.get_document_dependencies().values()

        ndi_mocdocs[0].data['base']['name'] = 'AAA'
        ndi_mocdocs[0].save_updates()

        assert not any([d.data['base']['name'] == 'AAA' for d in docs_from_db])
        assert any([d.current.data['base']['name'] == 'AAA' for d in docs_from_db])

    def test_update_by_id(self, experiment, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            experiment.add_document(ndi_doc)

        docs_from_db = experiment.get_document_dependencies().values()

        target_id = ndi_mocdocs[0].data['base']['id']
        experiment.ctx.db.update_by_id(target_id, { 'base': { 'name': 'AAAA' } })

        assert any([d.current.data['base']['name'] == 'AAAA' for d in docs_from_db])

    def test_update_many(self, experiment, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            experiment.add_document(ndi_doc)

        docs_from_db = experiment.get_document_dependencies().values()

        by_session_id = Q('base.session_id') == experiment.id
        experiment.ctx.db.update_many(by_session_id, { 'base': { 'version': '2' } })

        assert all([d.current.data['base']['version'] == '2' for d in docs_from_db])

    def test_upsert(self, experiment, ndi_mocdocs):
        doc = ndi_mocdocs[0]

        doc_from_db = experiment.ctx.db.find_by_id(doc.id)
        assert not doc_from_db

        experiment.ctx.db.upsert(doc)

        doc_from_db = experiment.ctx.db.find_by_id(doc.id)
        assert doc_from_db.data['base']['name'] == 'A'

        doc.data['base']['name'] = 'AAA'
        experiment.ctx.db.upsert(doc)

        assert doc_from_db.current.data['base']['name'] == 'AAA'