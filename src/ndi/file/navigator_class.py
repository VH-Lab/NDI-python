import os
from ..ido import Ido as IDO
from ..epoch.epochset import Param as EpochSetParam
from ..documentservice import DocumentService
from ..database.ingestion_help import IngestionHelp
from ..util.vlt import file as vlt_file
from ..util.vlt import data as vlt_data
from ..time import clocktype

class Navigator(IDO, EpochSetParam, DocumentService, IngestionHelp):
    """
    An object for accessing files on disk.
    """

    def __init__(self, session, fileparameters=None, epochprobemap_class=None, epochprobemap_fileparameters=None):
        """
        Creates a new Navigator object.
        """
        super().__init__()
        self.session = session
        self.fileparameters = fileparameters if fileparameters else {}
        self.epochprobemap_class = epochprobemap_class if epochprobemap_class else 'ndi.epoch.epochprobemap_daqsystem'
        self.epochprobemap_fileparameters = epochprobemap_fileparameters if epochprobemap_fileparameters else {}
        self.cached_epochfilenames = {}

    def buildepochtable(self):
        """
        Builds and returns an epoch table for the navigator.
        """
        all_epochs, epochprobemaps = self.selectfilegroups()

        et = []

        for i, epoch_files in enumerate(all_epochs):
            et_here = vlt_data.emptystruct('epoch_number', 'epoch_id', 'epoch_session_id', 'epochprobemap', 'epoch_clock', 't0_t1', 'underlying_epochs')

            underlying_epochs = vlt_data.emptystruct('underlying', 'epoch_id', 'epoch_session_id', 'epochprobemap', 'epoch_clock', 't0_t1')
            underlying_epochs['underlying'] = epoch_files
            underlying_epochs['epoch_id'] = self.epochid(i + 1, epoch_files)
            underlying_epochs['epoch_session_id'] = self.session.id()
            underlying_epochs['epoch_clock'] = [clocktype.ClockType('no_time')]
            underlying_epochs['t0_t1'] = [[float('nan'), float('nan')]]

            et_here['underlying_epochs'] = underlying_epochs
            et_here['epoch_number'] = i + 1
            et_here['epochprobemap'] = epochprobemaps[i] if epochprobemaps and i < len(epochprobemaps) else self.getepochprobemap(i + 1, epoch_files)
            et_here['epoch_clock'] = self.epochclock(i + 1)
            et_here['t0_t1'] = self.t0_t1(i + 1)
            et_here['epoch_id'] = self.epochid(i + 1, epoch_files)
            et_here['epoch_session_id'] = self.session.id()

            et.append(et_here)

        return et

    def selectfilegroups(self):
        """
        Selects groups of files that will comprise epochs.
        """
        # For now, just use the file matching parameters
        if 'filematch' in self.fileparameters:
            epochfiles_disk = vlt_file.findfilegroups(self.session.getpath(), self.fileparameters['filematch'])
            # drop hidden files
            hidden = []
            for i, epoch in enumerate(epochfiles_disk):
                for f in epoch:
                    if os.path.basename(f).startswith('.'):
                        hidden.append(i)
                        break
            epochfiles_disk = [epoch for i, epoch in enumerate(epochfiles_disk) if i not in hidden]

            return epochfiles_disk, [None] * len(epochfiles_disk)
        return [], []

    def getepochfiles(self, epoch_number_or_id):
        """
        Returns the file paths for one recording epoch.
        """
        et = self.epochtable()
        if isinstance(epoch_number_or_id, int):
            if 1 <= epoch_number_or_id <= len(et):
                return et[epoch_number_or_id - 1]['underlying_epochs']['underlying']
            else:
                raise ValueError(f"No such epoch number: {epoch_number_or_id}")
        elif isinstance(epoch_number_or_id, str):
            for entry in et:
                if entry['epoch_id'] == epoch_number_or_id:
                    return entry['underlying_epochs']['underlying']
            raise ValueError(f"No such epoch id: {epoch_number_or_id}")
        else:
            raise TypeError("epoch_number_or_id must be an int or a str.")

    def epochid(self, epoch_number, epochfiles):
        """
        Returns the epoch identifier for a particular epoch.
        """
        # Simplified implementation for now
        return f"epoch_{epoch_number}"

    def getepochprobemap(self, N, epochfiles):
        # Placeholder
        return None

    def epochclock(self, N):
        # Placeholder
        return [clocktype.ClockType('no_time')]

    def t0_t1(self, N):
        # Placeholder
        return [[float('nan'), float('nan')]]

    def numepochs(self):
        """
        Returns the number of epochs.
        """
        return len(self.epochtable())
