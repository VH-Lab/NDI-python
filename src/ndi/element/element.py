from ..ido import Ido
from ..epoch.epochset import EpochSet
from ..documentservice import DocumentService

class Element(Ido, EpochSet, DocumentService):
    def __init__(self, session, name, reference, type, underlying_element, direct, subject_id, dependencies):
        super().__init__()
        self.session = session
        self.name = name
        self.reference = reference
        self.type = type
        self.underlying_element = underlying_element
        self.direct = direct
        self.subject_id = subject_id
        self.dependencies = dependencies

    def is_sync_graph_root(self):
        return self.underlying_element is None

    def epochsetname(self):
        return f"element: {self.elementstring()}"

    def epoch_clock(self, epoch_number):
        et = self.epoch_table_entry(epoch_number)
        return et['epoch_clock']

    def t0_t1(self, epoch_number):
        et = self.epoch_table_entry(epoch_number)
        return et['t0_t1']

    def get_cache(self):
        if self.session:
            return self.session.cache, f"{self.elementstring()} | {self.type}"
        return None, None

    def build_epoch_table(self):
        # implementation will go here
        return []

    def elementstring(self):
        return f"{self.name} | {self.reference}"

    def add_epoch(self, epochid, epochclock, t0_t1, add_to_db=False, epochids=None):
        pass

    def load_added_epochs(self):
        pass

    def load_element_doc(self):
        pass

    def id(self):
        element_doc = self.load_element_doc()
        if not element_doc:
            raise ValueError("No element document.")
        return element_doc.id()

    def load_all_element_docs(self):
        pass

    def __eq__(self, other):
        if not isinstance(other, Element):
            return NotImplemented
        return (self.session == other.session and
                self.elementstring() == other.elementstring() and
                self.type == other.type)

    def new_document(self):
        pass

    def search_query(self, epochid=None):
        pass
