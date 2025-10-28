from ..ido import Ido
from ..epoch.epochset_param import EpochSetParam
from ..documentservice import DocumentService
import hashlib

class Navigator(Ido, EpochSetParam, DocumentService):
    def __init__(self, session, fileparameters=None, epochprobemap_class='ndi.epoch.epochprobemap_daqsystem', epochprobemap_fileparameters=None):
        super().__init__()
        self.session = session
        self.fileparameters = fileparameters if fileparameters is not None else {}
        self.epochprobemap_class = epochprobemap_class
        self.epochprobemap_fileparameters = epochprobemap_fileparameters if epochprobemap_fileparameters is not None else {}
        self.cached_epochfilenames = {}

    def __eq__(self, other):
        if not isinstance(other, Navigator):
            return NotImplemented
        return (self.session == other.session and
                self.fileparameters == other.fileparameters and
                self.epochprobemap_class == other.epochprobemap_class and
                self.epochprobemap_fileparameters == other.epochprobemap_fileparameters)

    def get_cache(self):
        if self.session:
            return self.session.cache, f'filenavigator_{self.id()}'
        return None, None

    def build_epoch_table(self):
        # implementation will go here
        return []

    def get_epoch_ingested_doc(self, epochfiles):
        # implementation will go here
        return None

    def epoch_id(self, epoch_number, epochfiles=None):
        # implementation will go here
        return ''

    def epoch_id_filename(self, number, epochfiles=None):
        # implementation will go here
        return ''

    def epochprobemap_filename(self, number):
        # implementation will go here
        return ''

    def default_epochprobemap_filename(self, number):
        # implementation will go here
        return ''

    def set_file_parameters(self, thefileparameters):
        self.fileparameters = thefileparameters

    def set_epoch_probemap_file_parameters(self, theepochprobemapfileparameters):
        self.epochprobemap_fileparameters = theepochprobemapfileparameters

    def path(self):
        return self.session.get_path()

    def select_file_groups_disk(self):
        # implementation will go here
        return []

    def select_file_groups(self):
        # implementation will go here
        return [], []

    def get_epoch_files(self, epoch_number_or_id):
        # implementation will go here
        return [], []

    def get_epoch_files_number(self, epoch_number):
        # implementation will go here
        return []

    def filematch_hashstring(self):
        if not self.fileparameters:
            return ''
        s = str(self.fileparameters.get('filematch', ''))
        return hashlib.md5(s.encode('utf-8')).hexdigest()

    def set_session(self, session):
        self.session = session

    def ingest(self):
        # implementation will go here
        return []

    def find_ingested_documents(self):
        # implementation will go here
        return []

    def new_document(self):
        # implementation will go here
        pass

    def search_query(self):
        # implementation will go here
        pass
