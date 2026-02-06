from .ido import Ido
from .documentservice import DocumentService
from .query import Query
from .database import fun as database_fun
from .time.syncgraph import SyncGraph
from .cache import Cache

class Session(Ido, DocumentService):
    def __init__(self, reference):
        super().__init__()
        self.reference = reference
        self.syncgraph = SyncGraph(self)
        self.cache = Cache()
        self.database = None

    @staticmethod
    def empty_id():
        return '00000000-0000-0000-0000-000000000000'

    def new_document(self, document_type='base', **kwargs):
        kwargs['base.session_id'] = self.id()
        return super().new_document(document_type, **kwargs)

    def search_query(self):
        return Query('base.session_id', 'exact_string', self.id(), '')

    def daqsystem_add(self, dev):
        dev.set_session(self)
        sq = dev.search_query()
        search_result = self.database_search(sq)
        if not search_result:
            doc_set = dev.new_document()
            self.database_add(doc_set)
        else:
            raise ValueError("dev or dev with same name already exists in the database.")

    def daqsystem_rm(self, dev):
        pass

    def daqsystem_load(self, **kwargs):
        q = Query('', 'isa', 'daqsystem', '') & self.search_query()
        if kwargs:
            for k, v in kwargs.items():
                if k.lower() == 'name':
                    k = 'base.name'
                q &= Query(k, 'exact_string', v, '')

        dev_doc = self.database_search(q)
        devs = [database_fun.ndi_document2ndi_object(doc, self) for doc in dev_doc]

        if len(devs) == 1:
            return devs[0]
        return devs

    def daqsystem_clear(self):
        devs = self.daqsystem_load(name='.*')
        if not isinstance(devs, list):
            devs = [devs]
        for dev in devs:
            self.daqsystem_rm(dev)

    def database_add(self, document):
        if not isinstance(document, list):
            document = [document]

        for doc in document:
            if doc.document_properties['base']['session_id'] == self.empty_id():
                doc.set_session_id(self.id())

        self.database.add(document)

    def database_rm(self, doc_unique_id, **kwargs):
        pass

    def database_search(self, searchparameters):
        in_session = Query('base.session_id', 'exact_string', self.id(), '')
        return self.database.search(searchparameters & in_session)

    def database_clear(self, areyousure):
        self.database.clear(areyousure)

    def validate_documents(self, document):
        pass

    def database_openbinarydoc(self, ndi_document_or_id, filename):
        return self.database.openbinarydoc(ndi_document_or_id, filename)

    def database_existbinarydoc(self, ndi_document_or_id, filename):
        return self.database.existbinarydoc(ndi_document_or_id, filename)

    def database_closebinarydoc(self, ndi_binarydoc_obj):
        return self.database.closebinarydoc(ndi_binarydoc_obj)

    def syncgraph_addrule(self, rule):
        pass

    def syncgraph_rmrule(self, index):
        pass

    def ingest(self):
        pass

    def get_ingested_docs(self):
        pass

    def is_fully_ingested(self):
        pass

    def get_path(self):
        return None

    def find_exp_obj(self, obj_name, obj_classname):
        pass

    def get_probes(self, *args, **kwargs):
        pass

    def get_elements(self, *args, **kwargs):
        pass

    def __eq__(self, other):
        if not isinstance(other, Session):
            return NotImplemented
        return self.id() == other.id()

    def creator_args(self):
        return [self.reference]
