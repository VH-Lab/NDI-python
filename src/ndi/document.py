from did.document import Document
from .ido import Ido
import ndi.fun.timestamp
from .util.vlt import data as vlt_data
import json
import os

class Document(Document):
    def __init__(self, document_type, **kwargs):
        if isinstance(document_type, dict):
            self.document_properties = document_type
        elif isinstance(document_type, Document):
            self.document_properties = document_type.document_properties
        else:
            self.document_properties = self.read_blank_definition(document_type)
            ido = Ido()
            self.document_properties['base']['id'] = ido.id()
            self.document_properties['base']['datestamp'] = ndi.fun.timestamp.timestamp()

            for key, value in kwargs.items():
                keys = key.split('.')
                d = self.document_properties
                for k in keys[:-1]:
                    d = d.setdefault(k, {})
                d[keys[-1]] = value

    def set_session_id(self, session_id):
        self.document_properties['base']['session_id'] = session_id

    def to_table(self):
        s = self.document_properties.copy()
        if 'depends_on' in s:
            del s['depends_on']
        if 'files' in s:
            del s['files']

        # This will require pandas, which is not yet a dependency
        # For now, I'll just return the flattened dictionary
        return vlt_data.flattenstruct2table(s)

    def doc_isa(self, document_class):
        sc = self.doc_superclass()
        c = self.doc_class()
        return document_class in [c] + sc

    def doc_class(self):
        return self.document_properties['document_class']['class_name']

    def doc_superclass(self):
        sc = []
        for superclass in self.document_properties['document_class']['superclasses']:
            s = Document(superclass['definition'])
            sc.append(s.doc_class())
        return list(set(sc))
