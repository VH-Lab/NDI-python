import json
import uuid
from did.document import Document as DIDDocument
from ..fun.timestamp import timestamp
from ..util.vlt import data as vlt_data

class Document(DIDDocument):
    def __init__(self, document_type, **kwargs):
        # NDI's document class expects to be able to pass kwargs to set properties
        # The DIDDocument class handles this through its options parameter

        # We need to initialize the DIDDocument first, then we can set the NDI-specific properties
        super().__init__(document_type, **kwargs)

        # Now, we can add the NDI-specific fields if we're creating a new document
        if not isinstance(document_type, dict) and not isinstance(document_type, DIDDocument):
            self.document_properties.setdefault('base', {})['datestamp'] = timestamp()


    def set_session_id(self, session_id):
        self.document_properties.setdefault('base', {})['session_id'] = session_id

    def id(self):
        return self.document_properties.get('base', {}).get('id')

    def session_id(self):
        return self.document_properties.get('base', {}).get('session_id')

    def __eq__(self, other):
        if not isinstance(other, Document):
            return NotImplemented
        return self.id() == other.id()

    def dependency(self):
        deps = self.document_properties.get('depends_on', [])
        names = [d['name'] for d in deps]
        return names, deps

    def dependency_value(self, dependency_name, error_if_not_found=True):
        deps = self.document_properties.get('depends_on', [])
        for d in deps:
            if d['name'] == dependency_name:
                return d['value']
        if error_if_not_found:
            raise ValueError(f"Dependency '{dependency_name}' not found.")
        return None

    def set_dependency_value(self, dependency_name, value, error_if_not_found=True):
        deps = self.document_properties.setdefault('depends_on', [])
        for d in deps:
            if d['name'] == dependency_name:
                d['value'] = value
                return

        if not error_if_not_found:
            deps.append({'name': dependency_name, 'value': value})
        else:
            raise ValueError(f"Dependency '{dependency_name}' not found.")

    def __add__(self, other):
        # Port of the 'plus' method
        new_doc = Document(self.document_properties.copy())

        # Merge superclasses
        sc_a = new_doc.document_properties.setdefault('document_class', {}).setdefault('superclasses', [])
        sc_b = other.document_properties.get('document_class', {}).get('superclasses', [])
        sc_a.extend(sc_b)

        other_props = other.document_properties.copy()
        other_props.pop('document_class', None)

        # Merge other properties
        new_doc.document_properties = vlt_data.struct_merge(new_doc.document_properties, other_props)
        return new_doc

    # We will rely on the DIDDocument's implementation of readblankdefinition for now
