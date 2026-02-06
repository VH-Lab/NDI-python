from ..element.element import Element
import abc

class Probe(Element, abc.ABC):
    def __init__(self, session, name, reference, type, subject_id):
        super().__init__(session, name, reference, type, None, True, subject_id, {})

    def buildepochtable(self):
        return self.session.getepochprobemap(self.reference)

    def epoch_clock(self, epoch_number):
        et = self.epoch_table_entry(epoch_number)
        return et['epoch_clock']

    def is_sync_graph_root(self):
        return False

    def epochsetname(self):
        return f"probe: {self.elementstring()}"

    def probestring(self):
        return f"{self.name} _ {self.reference}"

    def getchanneldevinfo(self, epoch_number_or_id):
        entry = self.epoch_table_entry(epoch_number_or_id)
        if entry is None:
            return None, None, None, None, None

        probemap = entry['epochprobemap']

        devices = [self.session.daqsystem_load(name) for name in probemap['devicestring']]
        devicenames = probemap['devicestring']
        devepochs = probemap['devepoch']
        channeltypes = probemap['channeltype']
        channels = probemap['channel']

        return devices, devicenames, devepochs, channeltypes, channels

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
