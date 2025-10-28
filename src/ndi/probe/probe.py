from ..element.element import Element

class Probe(Element):
    def __init__(self, session, name, reference, type, subject_id):
        super().__init__(session, name, reference, type, None, True, subject_id, {})

    def build_epoch_table(self):
        # implementation will go here
        return []

    def epoch_clock(self, epoch_number):
        et = self.epoch_table_entry(epoch_number)
        return et['epoch_clock']

    def is_sync_graph_root(self):
        return False

    def epochsetname(self):
        return f"probe: {self.elementstring()}"

    def probestring(self):
        return f"{self.name} _ {self.reference}"

    def get_channel_dev_info(self, epoch_number_or_id):
        pass

    def epoch_probemap_match(self, epochprobemap):
        return (self.name == epochprobemap['name'] and
                self.reference == epochprobemap['reference'] and
                self.type.lower() == epochprobemap['type'].lower())

    def __eq__(self, other):
        if not isinstance(other, Probe):
            return NotImplemented
        return (self.session == other.session and
                self.elementstring() == other.elementstring() and
                self.type == other.type)
