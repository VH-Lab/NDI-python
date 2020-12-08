from ndi import Session, Document
from ndi import Document as NDIDocument
from did import DID, DIDDocument, Query as Q
from did.database import SQL
import pytest
import json
from copy import deepcopy

mock_document_data = [
    {
        'base': {
            'id': None,
            'session_id': '2387492',
            'name': 'A',
            'datestamp': '2020-10-28T08:12:20+0000',
            'snapshots': [],
            'records': [],
        },
        'depends_on': [],
        'dependencies': [],
        'binary_files': [],
        'document_class': {
            'definition': '$NDIDOCUMENTPATH\/ndi_document_app.json',
            'validation': '$NDISCHEMAPATH\/ndi_document_app_schema.json',
            'name': 'ndi_document_app',
            'property_list_name': 'app',
            'class_version': '1',
            'superclasses': [{
                'definition': '$NDIDOCUMENTPATH\/base_document.json'
            }],
        },
        'app': {
            'a': True,
            'b': True
        },
    },
    {
        'base': {
            'id': None,
            'session_id': '2387492',
            'name': 'B',
            'datestamp': '2020-10-28T08:12:20+0000',
            'snapshots': [],
            'records': [],
        },
        'depends_on': [],
        'dependencies': [],
        'binary_files': [],
        'document_class': {
            'definition': '$NDIDOCUMENTPATH\/ndi_document_app.json',
            'validation': '$NDISCHEMAPATH\/ndi_document_app_schema.json',
            'name': 'ndi_document_app',
            'property_list_name': 'app',
            'class_version': '1',
            'superclasses': [{
                'definition': '$NDIDOCUMENTPATH\/base_document.json'
            }],
        },
        'app': {
            'a': True,
            'b': False
        },
    },
    {
        'base': {
            'id': None,
            'session_id': '2387492',
            'name': 'C',
            'datestamp': '2020-10-28T08:12:20+0000',
            'snapshots': [],
            'records': [],
        },
        'depends_on': [],
        'dependencies': [],
        'binary_files': [],
        'document_class': {
            'definition': '$NDIDOCUMENTPATH\/ndi_document_app.json',
            'validation': '$NDISCHEMAPATH\/ndi_document_app_schema.json',
            'name': 'ndi_document_app',
            'property_list_name': 'app',
            'class_version': '1',
            'superclasses': [{
                'definition': '$NDIDOCUMENTPATH\/base_document.json'
            }],
        },
        'app': {
            'a': False,
            'b': False
        },
    },
]

@pytest.fixture
def session():
    did = DID(
        driver = SQL(
            'postgres://postgres:password@localhost:5432/ndi_did_sql_tests', 
            hard_reset_on_init = True,
            debug_mode = False,
            verbose_feedback = True,
        ),
        binary_directory = './tests/database/sql/test_crud'
    )
    yield Session('test_sql_crud').connect(
        data_interface_database = did,
        load_existing=False
    )
    did.driver.connection.close()

@pytest.fixture
def ndi_mocdocs():
    # names are 'A', 'B', and 'C'
    yield [NDIDocument(data) for data in deepcopy(mock_document_data)]

def doc_count(ctx_carrier):
    return list(ctx_carrier.ctx._did_adapter.did.driver.execute('select count(*) from document;'))[0][0]

def find_docs(ctx_carrier, where_clause = ''):
    return ctx_carrier.ctx._did_adapter.did.driver.execute(f'select data from document {where_clause};')

def get_snapshot(ctx_carrier):
    return ctx_carrier.ctx._did_adapter.did.driver.working_snapshot_id

class TestSqlCrud:
    def test_add(self, session, ndi_mocdocs):
        doc = ndi_mocdocs[0]
        session.add_document(doc, save=True)
        response = list(find_docs(
            session,
            f'where document_id = \'{ndi_mocdocs[0].id}\''
        ))
        assert len(response) is 1

        data = response[0][0]
        assert data['base']['session_id'] == session.id

    def test_add_duplicate(self, session, ndi_mocdocs):
        session.add_document(ndi_mocdocs[0], save=True)
        try:
            doc_count_before = doc_count(session)
            session.add_document(ndi_mocdocs[0], save=True)
            # if this call succeeds, test should fail
            assert False
        except RuntimeError as error:
            assert str(error).startswith('Dependency name is already in use (depen')
            doc_count_after = doc_count(session)
            assert doc_count_before == doc_count_after

    def test_find_by_id(self, session, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            session.add_document(ndi_doc)
        
        # get_document_dependencies() makes calls to find_by_id
        document_dependencies = session.get_document_dependencies()
        assert len(ndi_mocdocs) == len(document_dependencies)
        for name, ndi_doc in document_dependencies.items():
            assert any([d.data['base']['name'] == name for d in ndi_mocdocs])

    def test_find(self, session, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            session.add_document(ndi_doc)
        session.save()
        
        by_app_a = Q('app.a') == True
        found_ids = [doc.id for doc in session.find_documents(by_app_a)]
        expected_ids = [doc.id for doc in ndi_mocdocs if doc.data['app']['a'] == True]
        assert found_ids == expected_ids

        by_app_a_and_name = by_app_a & (Q('base.name') == 'A')
        found_ids = [doc.id for doc in session.find_documents(by_app_a_and_name)]
        expected_ids = [
            doc.id for doc in ndi_mocdocs
            if doc.data['app']['a'] == True
            and doc.data['base']['name'] == 'A'
        ]
        assert found_ids == expected_ids

    def test_update(self, session, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            session.add_document(ndi_doc)

        docs_from_db = session.get_document_dependencies().values()

        ndi_mocdocs[0].data['base']['name'] = 'AAA'
        ndi_mocdocs[0].update()

        assert not any([d.data['base']['name'] == 'AAA' for d in docs_from_db])
        assert any([d.current.data['base']['name'] == 'AAA' for d in docs_from_db])

    def test_update_by_id(self, session, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            session.add_document(ndi_doc)

        docs_from_db = session.get_document_dependencies().values()

        target_id = ndi_mocdocs[0].data['base']['id']
        session.ctx.did.update_by_id(target_id, { 'base': { 'name': 'AAAA' } })

        assert any([d.current.data['base']['name'] == 'AAAA' for d in docs_from_db])

    def test_update_many(self, session, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            session.add_document(ndi_doc)

        docs_from_db = session.get_document_dependencies().values()

        by_session_id = Q('base.session_id') == session.id
        session.ctx.did.update_many(by_session_id, { 'app': { 'd': True } })
        session.save()

        assert all([d.current.data['app']['d'] == True for d in docs_from_db])

    def test_upsert(self, session, ndi_mocdocs):
        doc = ndi_mocdocs[0]

        doc_from_db = session.ctx.did.find_by_id(doc.id)
        assert not doc_from_db

        session.ctx.did.upsert(doc)

        doc_from_db = session.ctx.did.find_by_id(doc.id)
        assert doc_from_db.data['base']['name'] == 'A'

        doc.data['base']['name'] = 'AAA'
        session.ctx.did.upsert(doc)

        assert doc_from_db.current.data['base']['name'] == 'AAA'

    def test_delete(self, session, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            session.add_document(ndi_doc)

        session_deps = session.get_document_dependencies()
        doc_on_session = session_deps[ndi_mocdocs[0].data['base']['name']]
        
        ndi_mocdocs[0].delete()

        # show that the original (and directly deleted) document instance is current
        assert ndi_mocdocs[0].deleted 
        assert ndi_mocdocs[0].data is None

        # show that the document instance attached to the session is current
        assert doc_on_session.current.deleted 
        assert doc_on_session.current.data is None

        # show that the document is no longer present in the db
        doc_from_db = session.ctx.did.find_by_id(ndi_mocdocs[0].id)
        assert doc_from_db is None

    def test_delete_by_id(self, session, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            session.add_document(ndi_doc)

        target_id = ndi_mocdocs[0].data['base']['id']
        session.ctx.did.delete_by_id(target_id)

        doc_from_db = session.ctx.did.find_by_id(ndi_mocdocs[0].id)
        assert doc_from_db is None

    def test_delete_many(self, session, ndi_mocdocs):
        for ndi_doc in ndi_mocdocs:
            session.add_document(ndi_doc)
        by_session_id = Q('base.session_id') == session.id
        session.ctx.did.delete_many(by_session_id)

        docs_from_db = session.get_document_dependencies().values()
        assert all([
            d is None or (d.current.deleted and d.current.data is None)
            for d in docs_from_db
        ])
        for doc in ndi_mocdocs:
            doc_from_db = session.ctx.did.find_by_id(doc.id)
            assert doc_from_db is None

