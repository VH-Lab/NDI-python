from __future__ import annotations
import ndi.types as T
from did import DIDDocument
import ndi

class DIDAdapter: 
    def __init__(self, ctx, database):
        self.ctx = ctx
        self.database = database

    def find(self, did_query=None):
        did_docs = self.database.find(query=did_query)
        return [self._did_to_ndi_doc(d) for d in did_docs]

    def add(self, ndi_document, save=True) -> None:
        did_document = DIDDocument(ndi_document.data)
        return self.database.add(did_document, save=save)

    def update(self, ndi_document, save=True, force = False) -> None:
        did_document = DIDDocument(ndi_document.data)
        self.database.update(did_document, save=save)

    def upsert(self, ndi_document, save=True, force = False) -> None:
        did_document = DIDDocument(ndi_document.data)
        self.database.upsert(did_document, save=save)

    def delete(self, ndi_document, save=True, force = False) -> None:
        pass

    def find_by_id(self, id_):
        did_doc = self.database.find_by_id(id_)
        if did_doc:
            return self._did_to_ndi_doc(did_doc)

    def update_by_id(self, id_, payload={}, save=True, force = False) -> None:
        self.database.update_by_id(id_, payload, save=save)

    def delete_by_id(self, id_, save=True, force = False) -> None:
        pass

    def update_many(self, did_query=None, payload={}, save=True, force = False) -> None:
        self.database.update_many(did_query, payload, save=save)

    def delete_many(self, did_query=None, save=True, force = False) -> None:
        pass

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