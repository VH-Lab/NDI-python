class SyncOptions:
    """
    Options class for controlling sync behavior.
    """

    def __init__(self, **kwargs):
        """
        Initializes the SyncOptions object.

        Args:
            SyncFiles (bool): If true, files will be downloaded (default: False).
            Verbose (bool): If true, verbose output is printed (default: True).
            DryRun (bool): If true, actions are simulated but not performed (default: False).
            FileUploadStrategy (str): "serial" or "batch" (default: "batch").
        """
        self.SyncFiles = kwargs.get('SyncFiles', False)
        self.Verbose = kwargs.get('Verbose', True)
        self.DryRun = kwargs.get('DryRun', False)
        self.FileUploadStrategy = kwargs.get('FileUploadStrategy', 'batch')

        if self.FileUploadStrategy not in ['serial', 'batch']:
            raise ValueError("FileUploadStrategy must be either 'serial' or 'batch'")

    def to_dict(self):
        """
        Convert properties to a dictionary.
        """
        return {
            'SyncFiles': self.SyncFiles,
            'Verbose': self.Verbose,
            'DryRun': self.DryRun,
            'FileUploadStrategy': self.FileUploadStrategy
        }
