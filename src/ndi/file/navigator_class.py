from ..ido import Ido
from ..epoch.epochset import Param as EpochSet
from ..documentservice import DocumentService
# from ..database.ingestion_help import IngestionHelp # This class needs to be ported

class Navigator(Ido, EpochSet, DocumentService): #, IngestionHelp):
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
            return self.session.cache, f"filenavigator_{self.id()}"
        return None, None

    def buildepochtable(self):
        # implementation will go here
        return []

    def getepochprobemap(self, n, epochfiles=None):
        # implementation will go here
        pass

    def getepochingesteddoc(self, epochfiles):
        # implementation will go here
        pass

    def epochid(self, epoch_number, epochfiles=None):
        # implementation will go here
        pass

    def epochidfilename(self, number, epochfiles=None):
        # implementation will go here
        pass

    def epochprobemapfilename(self, number):
        # implementation will go here
        pass

    def defaultepochprobemapfilename(self, number):
        # implementation will go here
        pass

    def path(self):
        return self.session.get_path()

    def selectfilegroups_disk(self):
        # implementation will go here
        return []

    def selectfilegroups(self):
        # implementation will go here
        return [], []

    def getepochfiles(self, epoch_number_or_id):
        # implementation will go here
        pass

    def getepochfiles_number(self, epoch_number):
        # implementation will go here
        pass

    def filematch_hashstring(self):
        # implementation will go here
        pass

    def newdocument(self):
        # implementation will go here
        pass

    def searchquery(self):
        # implementation will go here
        pass
