import os

class PathConstants:
    @staticmethod
    def root_folder():
        """
        Returns the root folder of the NDI distribution.
        """
        # Assuming this file is in src/ndi/common/path_constants.py
        # Root is src/ndi/
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @staticmethod
    def common_folder():
        """
        Returns the path to the package ndi_common resources.
        """
        return os.path.join(PathConstants.root_folder(), 'resources', 'ndi_common')
