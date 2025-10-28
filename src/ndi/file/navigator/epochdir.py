from .navigator import Navigator
from ...util.vlt import file as vlt_file
import os

class EpochDir(Navigator):
    def __init__(self, session, fileparameters=None, epochprobemap_class='ndi.epoch.epochprobemap_daqsystem', epochprobemap_fileparameters=None):
        super().__init__(session, fileparameters, epochprobemap_class, epochprobemap_fileparameters)

    def epoch_id(self, epoch_number, epochfiles=None):
        if epochfiles is None:
            epochfiles = self.get_epoch_files(epoch_number)

        if self.is_ingested(epochfiles):
            return self.ingested_files_epoch_id(epochfiles)
        else:
            pathdir = os.path.dirname(epochfiles[0])
            return os.path.basename(pathdir)

    def select_file_groups_disk(self):
        exp_path = self.path()
        return vlt_file.findfilegroups(exp_path, self.fileparameters['filematch'], SearchParent=False, SearchDepth=1)
