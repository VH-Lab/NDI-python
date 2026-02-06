import abc

class Database(abc.ABC):
    def __init__(self, path, session_unique_reference):
        self.path = path
        self.session_unique_reference = session_unique_reference

    def open(self):
        return self.do_open_database()

    def new_document(self, document_type='base'):
        # This will depend on the ndi.document class
        pass

    def add(self, ndi_document_obj, update=True):
        add_parameters = {'update': update}
        return self.do_add(ndi_document_obj, add_parameters)

    def read(self, ndi_document_id):
        return self.do_read(ndi_document_id)

    def openbinarydoc(self, ndi_document_or_id, filename):
        # implementation will go here
        pass

    def existbinarydoc(self, ndi_document_or_id, filename):
        # implementation will go here
        pass

    def closebinarydoc(self, ndi_binarydoc_obj):
        # implementation will go here
        pass

    def remove(self, ndi_document_id):
        # implementation will go here
        pass

    def alldocids(self):
        # needs to be overridden
        return []

    def clear(self, areyousure='no'):
        # implementation will go here
        pass

    def search(self, searchparams):
        # implementation will go here
        pass

    # Protected methods
    @abc.abstractmethod
    def do_add(self, ndi_document_obj, add_parameters):
        pass

    @abc.abstractmethod
    def do_read(self, ndi_document_id):
        pass

    @abc.abstractmethod
    def do_remove(self, ndi_document_id):
        pass

    @abc.abstractmethod
    def do_search(self, searchoptions, searchparams):
        pass

    @abc.abstractmethod
    def do_openbinarydoc(self, ndi_document_id):
        pass

    @abc.abstractmethod
    def check_exist_binarydoc(self, ndi_document_id):
        pass

    @abc.abstractmethod
    def do_closebinarydoc(self, ndi_binarydoc_obj):
        pass

    @abc.abstractmethod
    def do_open_database(self):
        pass
