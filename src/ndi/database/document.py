from did.document import Document as DidDocument
from ..ido import Ido as IDO
import ndi.fun.timestamp
from ..util.vlt import data as vlt_data

class Document(DidDocument):
    """
    An NDI database document.
    """

    def __init__(self, document_type, **kwargs):
        super().__init__(document_type, **kwargs)
        # NDI-specific initializations can go here

    def to_table(self):
        """
        Converts the document to a table.
        """
        s = self.document_properties.copy()
        if 'depends_on' in s:
            del s['depends_on']
        if 'files' in s:
            del s['files']

        # This will require pandas, which is not yet a dependency
        # For now, I'll just return the flattened dictionary
        return vlt_data.flattenstruct2table(s)
