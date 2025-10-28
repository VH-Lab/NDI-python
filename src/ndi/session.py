from .ido import Ido
from .documentservice import DocumentService

class Session(Ido, DocumentService):
    def __init__(self, reference):
        super().__init__()
        self.reference = reference
        # self.syncgraph = ndi.time.syncgraph(self)
        # self.cache = ndi.cache()
        # self.database = None

    def search_query(self):
        return {'base.session_id': self.id()}

    def daqsystem_add(self, dev):
        pass

    def daqsystem_rm(self, dev):
        pass

    def daqsystem_load(self, **kwargs):
        pass

    def daqsystem_clear(self):
        pass

    def database_add(self, document):
        pass

    def database_rm(self, doc_unique_id, **kwargs):
        pass

    def database_search(self, searchparameters):
        pass

    def database_clear(self, areyousure):
        pass

    def validate_documents(self, document):
        pass

    def database_openbinarydoc(self, ndi_document_or_id, filename):
        pass

    def database_existbinarydoc(self, ndi_document_or_id, filename):
        pass

    def database_closebinarydoc(self, ndi_binarydoc_obj):
        pass

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
