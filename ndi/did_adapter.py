from __future__ import annotations
import ndi.types as T
from did import DIDDocument
import ndi

class DIDAdapter: 
    def __init__(self, ctx, database):
        self.ctx = ctx
        self.database = database
    
    def save(self):
        self.database.save()
    
    def revert(self):
        self.database.revert()
    
    def get_history(self):
        self.database.get_history()

    def add(self, ndi_document, save=None) -> None:
        did_document = DIDDocument(ndi_document.data)
        return self.database.add(did_document, save=save)

    def find(self, did_query=None, snapshot=None, commit=None, in_all_history=False):
        did_docs = self.database.find(query=did_query, snapshot=snapshot, commit=commit, in_all_history=in_all_history)
        return [self._did_to_ndi_doc(d) for d in did_docs]

    def find_by_id(self, id_, snapshot=None, commit=None, in_all_history=False):
        did_doc = self.database.find_by_id(id_, snapshot=snapshot, commit=commit, in_all_history=in_all_history)
        if did_doc:
            return self._did_to_ndi_doc(did_doc)

    def find_record(self, record, snapshot=None, commit=None, in_all_history=False):
        did_doc = self.database.find_by_hash(record, snapshot=snapshot, commit=commit, in_all_history=in_all_history)
        if did_doc:
            return self._did_to_ndi_doc(did_doc)

    def update(self, ndi_document, save=None) -> None:
        did_document = DIDDocument(ndi_document.data)
        self.database.update(did_document, save=save)

    def upsert(self, ndi_document, save=None) -> None:
        did_document = DIDDocument(ndi_document.data)
        self.database.upsert(did_document, save=save)

    def update_by_id(self, id_, payload={}, save=None) -> None:
        self.database.update_by_id(id_, payload, save=save)

    def update_many(self, did_query=None, payload={}, save=None) -> None:
        self.database.update_many(did_query, payload, save=save)

    def update_record_dependencies(self, record, dependencies, save=None):
        self.database.update_dependencies(record, dependencies, save=save)

    def delete(self, ndi_document, save=None) -> None:
        did_document = DIDDocument(ndi_document.data)
        self.database.delete(did_document, save=save)

    def delete_by_id(self, id_, save=None) -> None:
        self.database.delete_by_id(id_, save=save)

    def delete_many(self, did_query=None, save=None) -> None:
        self.database.delete_many(did_query, save=save)

    def _did_to_ndi_doc(self, did_document):
        return ndi.Document(data=did_document.data).with_ctx(self.ctx)
    
    def __getattr__(self, name):
        """Forward calls that don't need modification to DID database.

        :param name: [description]
        :type name: [type]
        :return: [description]
        :rtype: [type]
        """
        return getattr(self.database, name)
