from ..navigator_class import Navigator
import os

class EpochDir(Navigator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def epochid(self, epoch_number, epochfiles=None):
        if epochfiles is None:
            epochfiles = self.getepochfiles(epoch_number)

        if self.is_ingested(epochfiles):
            return self.ingestedfiles_epochid(epochfiles)
        else:
            pathdir = os.path.dirname(epochfiles[0])
            return os.path.basename(pathdir)

    def selectfilegroups_disk(self):
        # This will require a Python implementation of findfilegroups
        # For now, we'll return an empty list
        return []
