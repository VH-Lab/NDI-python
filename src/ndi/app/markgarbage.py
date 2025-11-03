from .app import App
from ..time.timereference import TimeReference
from ..query import Query

class MarkGarbage(App):
    def __init__(self, session):
        super().__init__(session, 'ndi_app_markgarbage')

    def mark_valid_interval(self, epochset_obj, t0, timeref_t0, t1, timeref_t1):
        valid_interval = {
            'timeref_structt0': timeref_t0.ndi_timereference_struct(),
            't0': t0,
            'timeref_structt1': timeref_t1.ndi_timereference_struct(),
            't1': t1,
        }
        return self.save_valid_interval(epochset_obj, valid_interval)

    def save_valid_interval(self, epochset_obj, valid_interval_struct):
        # We need to implement a Python equivalent of vlt.data.eqlen for this to work

        vi, _ = self.load_valid_interval(epochset_obj)

        # This is a placeholder for the actual comparison logic
        # For now, we'll just append
        vi.append(valid_interval_struct)

        self.clear_valid_interval(epochset_obj)

        new_doc = self.session.new_document('valid_interval', valid_interval=vi)
        new_doc += self.new_document()
        new_doc.set_dependency_value('element_id', epochset_obj.id())
        self.session.database_add(new_doc)
        return True

    def clear_valid_interval(self, epochset_obj):
        _, mydoc = self.load_valid_interval(epochset_obj)
        if mydoc:
            self.session.database_rm(mydoc)
        return True

    def load_valid_interval(self, epochset_obj):
        vi = []
        searchq = Query(self.search_query()) & Query('', 'isa', 'valid_interval', '')

        # Assuming epochset_obj is an Element
        searchq2 = Query('', 'depends_on', 'element_id', epochset_obj.id())
        searchq = searchq & searchq2

        mydoc = self.session.database_search(searchq)

        if mydoc:
            for doc in mydoc:
                vi.extend(doc.document_properties['valid_interval'])

        # The logic for checking underlying elements needs to be added here

        return vi, mydoc

    def identify_valid_intervals(self, epochset_obj, timeref, t0, t1):
        # This is a complex method that will require more components to be ported.
        # For now, we'll return the full interval as valid.
        return [[t0, t1]]
