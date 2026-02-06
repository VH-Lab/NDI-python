from .document import Document

class Database:
    def __init__(self, path, session_unique_reference):
        self.path = path
        self.session_unique_reference = session_unique_reference

    def new_document(self, document_type='base'):
        return Document(document_type, **{'session_unique_refrence': self.session_unique_reference})

    def add(self, ndi_document_obj, update=True):
        self._do_add(ndi_document_obj, {'Update': update})

    def read(self, ndi_document_id):
        return self._do_read(ndi_document_id)

    def openbinarydoc(self, ndi_document_or_id, filename):
        if isinstance(ndi_document_or_id, Document):
            ndi_document_id = ndi_document_or_id.id()
        else:
            ndi_document_id = ndi_document_or_id

        ndi_document_obj = self.read(ndi_document_id)
        return self._do_openbinarydoc(ndi_document_id, filename)

    def existbinarydoc(self, ndi_document_or_id, filename):
        if isinstance(ndi_document_or_id, Document):
            ndi_document_id = ndi_document_or_id.id()
        else:
            ndi_document_id = ndi_document_or_id

        return self._check_exist_binarydoc(ndi_document_id, filename)

    def closebinarydoc(self, ndi_binarydoc_obj):
        return self._do_closebinarydoc(ndi_binarydoc_obj)

    def remove(self, ndi_document_id):
        if not isinstance(ndi_document_id, list):
            ndi_document_id = [ndi_document_id]

        for item in ndi_document_id:
            if isinstance(item, Document):
                self._do_remove(item.id())
            else:
                self._do_remove(item)

    def alldocids(self):
        raise NotImplementedError

    def clear(self, areyousure='no'):
        if areyousure.lower() == 'yes':
            ids = self.alldocids()
            for id in ids:
                self.remove(id)
        else:
            print("Not clearing because user did not indicate they are sure.")

    def search(self, searchparams):
        return self._do_search({}, searchparams)

    # Protected methods
    def _do_add(self, ndi_document_obj, add_parameters):
        raise NotImplementedError

    def _do_read(self, ndi_document_id):
        raise NotImplementedError

    def _do_remove(self, ndi_document_id):
        raise NotImplementedError

    def _do_search(self, searchoptions, searchparams):
        raise NotImplementedError

    def _do_openbinarydoc(self, ndi_document_id, filename):
        raise NotImplementedError

    def _check_exist_binarydoc(self, ndi_document_id, filename):
        raise NotImplementedError

    def _do_closebinarydoc(self, ndi_binarydoc_obj):
        raise NotImplementedError

    def _do_open_database(self):
        raise NotImplementedError
