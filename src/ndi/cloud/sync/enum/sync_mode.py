from enum import Enum
import importlib

class SyncMode(Enum):
    """
    Enumeration of supported dataset synchronization modes.
    """
    DownloadNew = "download_new"
    MirrorFromRemote = "mirror_from_remote"
    UploadNew = "upload_new"
    MirrorToRemote = "mirror_to_remote"
    TwoWaySync = "two_way_sync"

    def execute(self, ndi_dataset, sync_options):
        """
        Executes the synchronization function corresponding to the mode.

        Args:
            ndi_dataset: The NDI dataset object.
            sync_options: The SyncOptions object.
        """
        module_name = f"ndi.cloud.sync.{self.value}"
        try:
            module = importlib.import_module(module_name)
            func = getattr(module, self.value)
            return func(ndi_dataset, sync_options)
        except (ImportError, AttributeError) as e:
            raise NotImplementedError(f"Synchronization function '{self.value}' is not implemented.") from e
