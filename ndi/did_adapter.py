from __future__ import annotations
import ndi.types as T
from did import DIDDocument
import ndi

class DIDAdapter:
    """ Transformer: `NDIDocument`s <-> `DIDDocument`s. """
    def __init__(self, ctx, did):
        self.ctx = ctx
        self.did = did
    
    def save(self):
        self.did.save()
    
    def revert(self):
        self.did.revert()
    
    def get_history(self):
        return self.did.get_history()
    
    def get_working_snapshot(self):
        return self.did.driver.working_snapshot_id

    def add(self, ndi_document, save=None) -> None:
        did_document = DIDDocument(ndi_document.data)
        return self.did.add(did_document, save=save)

    def find(self, did_query=None, snapshot=None, commit=None, in_all_history=False):
        did_docs = self.did.find(query=did_query, snapshot=snapshot, commit=commit, in_all_history=in_all_history)
        return [self._did_to_ndi_doc(d) for d in did_docs]

    def find_by_id(self, id_, snapshot=None, commit=None, in_all_history=False):
        did_doc = self.did.find_by_id(id_, snapshot=snapshot, commit=commit, in_all_history=in_all_history)
        if did_doc:
            return self._did_to_ndi_doc(did_doc)

    def find_record(self, record, snapshot=None, commit=None, in_all_history=False):
        did_doc = self.did.find_by_hash(record, snapshot=snapshot, commit=commit, in_all_history=in_all_history)
        if did_doc:
            return self._did_to_ndi_doc(did_doc)

    def update(self, ndi_document, save=None) -> None:
        did_document = DIDDocument(ndi_document.data)
        self.did.update(did_document, save=save)

    def upsert(self, ndi_document, save=None) -> None:
        did_document = DIDDocument(ndi_document.data)
        self.did.upsert(did_document, save=save)

    def update_by_id(self, id_, payload={}, save=None) -> None:
        self.did.update_by_id(id_, payload, save=save)

    def update_many(self, did_query=None, payload={}, save=None) -> None:
        self.did.update_many(did_query, payload, save=save)

    def update_record_dependencies(self, record, dependencies, save=None):
        self.did.update_dependencies(record, dependencies, save=save)

    def delete(self, ndi_document, save=None) -> None:
        did_document = DIDDocument(ndi_document.data)
        self.did.delete(did_document, save=save)

    def delete_by_id(self, id_, save=None) -> None:
        self.did.delete_by_id(id_, save=save)

    def delete_many(self, did_query=None, save=None) -> None:
        self.did.delete_many(did_query, save=save)

    def _did_to_ndi_doc(self, did_document):
        return ndi.Document(data=did_document.data).with_ctx(self.ctx)
    
    def __getattr__(self, name):
        """Forward calls that don't need modification to DID did.

        :param name: [description]
        :type name: [type]
        :return: [description]
        :rtype: [type]
        """
        return getattr(self.did, name)
