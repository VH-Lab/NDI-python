from __future__ import annotations
import ndi.types as T
from did import DIDDocument

class DIDAdapter: 
    def __init__(self, database):
        self.database = database

    def find(self, ndi_query=None):
        pass

    def add(self, ndi_document, save=True) -> None:
        did_document = DIDDocument(ndi_document.data)
        return self.database.add(did_document, save=save)

    def update(self, ndi_document, save=True, force = False) -> None:
        pass

    def upsert(self, ndi_document, save=True, force = False) -> None:
        pass

    def delete(self, ndi_document, save=True, force = False) -> None:
        pass

    def find_by_id(self, id_):
        pass

    def update_by_id(self, id_, payload={}, save=True, force = False) -> None:
        pass

    def delete_by_id(self, id_, save=True, force = False) -> None:
        pass

    def update_many(self, ndi_query=None, payload={}, save=True, force = False) -> None:
        pass

    def delete_many(self, ndi_query=None, save=True, force = False) -> None:
        pass
    
    def __getattr__(self, name):
        """Forward calls that don't need modification to DID database.

        :param name: [description]
        :type name: [type]
        :return: [description]
        :rtype: [type]
        """
        return getattr(self.database, name)