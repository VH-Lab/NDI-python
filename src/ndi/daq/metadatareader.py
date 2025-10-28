from ..ido import Ido
from ..documentservice import DocumentService

class Metadatareader(Ido, DocumentService):
    def __init__(self, tsvfile_regexpression=''):
        super().__init__()
        self.tab_separated_file_parameter = tsvfile_regexpression

    def readmetadata(self, epochfiles):
        pass

    def readmetadata_ingested(self, epochfiles, s):
        pass

    def readmetadatafromfile(self, file):
        pass

    def ingest_epochfiles(self, epochfiles, epoch_id):
        pass

    def get_ingested_document(self, epochfiles, s):
        pass

    def __eq__(self, other):
        if not isinstance(other, Metadatareader):
            return NotImplemented
        return self.__class__ == other.__class__ and self.tab_separated_file_parameter == other.tab_separated_file_parameter

    def newdocument(self):
        pass

    def searchquery(self):
        pass
