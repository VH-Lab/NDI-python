from ..ido import Ido
from ..documentservice import DocumentService

class Reader(Ido, DocumentService):
    def __init__(self, session=None, doc=None):
        super().__init__()
        if session is not None and doc is not None:
            self.identifier = doc.document_properties['base']['id']

    def get_ingested_document(self, epochfiles, s):
        pass

    def ingested2epochs_t0t1_epochclock(self, s):
        pass

    def epoch_clock(self, epochfiles):
        return []

    def epoch_clock_ingested(self, epochfiles, s):
        pass

    def t0_t1(self, epochfiles):
        return []

    def t0_t1_ingested(self, epochfiles, s):
        pass

    def verify_epoch_probemap(self, epochprobemap, epochfiles):
        pass

    def ingest_epoch_files(self, epochfiles):
        pass

    def __eq__(self, other):
        if not isinstance(other, Reader):
            return NotImplemented
        return self.__class__ == other.__class__ and self.id() == other.id()

    def new_document(self):
        pass

    def search_query(self):
        pass
