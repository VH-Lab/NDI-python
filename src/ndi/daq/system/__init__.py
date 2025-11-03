from ...ido import Ido
from ...documentservice import DocumentService
from ...time.clocktype import ClockType
from ...util.vlt import data as vlt_data
from ..daqsystemstring import DaqSystemString

class System(Ido, DocumentService):
    def __init__(self, name, filenavigator, daqreader, daqmetadatareader=None):
        super().__init__()
        self.name = name
        self.filenavigator = filenavigator
        self.daqreader = daqreader
        self.daqmetadatareader = daqmetadatareader if daqmetadatareader is not None else []

    def set_daqmetadatareader(self, thedaqmetadatareaders):
        if not isinstance(thedaqmetadatareaders, list):
            raise TypeError("thedaqmetadatareaders must be a list.")
        for item in thedaqmetadatareaders:
            if not isinstance(item, Metadatareader):
                raise TypeError("All items in thedaqmetadatareaders must be of type Metadatareader.")
        self.daqmetadatareader = thedaqmetadatareaders

    def __eq__(self, other):
        if not isinstance(other, System):
            return NotImplemented
        return self.name == other.name and self.__class__ == other.__class__

    def epoch_clock(self, epoch_number):
        return [ClockType('no_time')]

    def t0_t1(self, epoch_number):
        return [[float('nan'), float('nan')]]

    def epoch_id(self, epoch_number):
        return self.filenavigator.epoch_id(epoch_number)

    def get_probes(self):
        et = self.epoch_table()
        probes_struct = []
        for n in range(len(et)):
            epc = et[n]['epochprobemap']
            if epc:
                for ec in range(len(epc)):
                    myprobemap = DaqSystemString(epc[ec]['devicestring'])
                    if myprobemap.devicename.lower() == self.name.lower():
                        newentry = {
                            'name': epc[ec]['name'],
                            'reference': epc[ec]['reference'],
                            'type': epc[ec]['type'],
                            'subject_id': epc[ec]['subjectstring']
                        }
                        probes_struct.append(newentry)

        # This part requires equnique, which is not ported yet.
        # For now, just return the list with potential duplicates.
        return probes_struct

    def session(self):
        return self.filenavigator.session

    def set_session(self, session):
        self.filenavigator.set_session(session)

    def delete_epoch(self, number, removedata):
        raise NotImplementedError

    def get_cache(self):
        if self.session():
            return self.session().cache, f"daqsystem_{self.id()}"
        return None, None

    def build_epoch_table(self):
        et = self.filenavigator.epoch_table()
        # The rest of this method depends on GUI components and other things not yet ported
        return et

    def epoch_probemap_filename(self, epochnumber):
        return self.filenavigator.epoch_probemap_filename(epochnumber)

    def verify_epoch_probemap(self, epochprobemap, epoch):
        epochfiles = self.filenavigator.get_epoch_files(epoch)
        return self.daqreader.verify_epoch_probemap(epochprobemap, epochfiles)

    def epoch_tag_filename(self, epochnumber):
        return self.filenavigator.epoch_tag_filename(epochnumber)

    def get_epoch_probemap(self, epoch, filenav_epochprobemap=None):
        # This logic is a bit tricky and depends on the daqreader implementation
        if filenav_epochprobemap:
            return filenav_epochprobemap
        return self.filenavigator.get_epoch_probemap(epoch)

    def get_metadata(self, epoch, channel):
        if not (1 <= channel <= len(self.daqmetadatareader)):
            raise ValueError("Metadata channel out of range.")
        epochfiles = self.filenavigator.get_epoch_files(epoch)
        # Ingested logic needs to be added here
        return self.daqmetadatareader[channel-1].readmetadata(epochfiles)

    def ingest(self):
        # Implementation depends on other classes
        pass

    def new_document(self):
        # Implementation depends on other classes
        pass

    def search_query(self):
        # Implementation depends on other classes
        pass
