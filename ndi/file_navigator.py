from __future__ import annotations
import ndi.types as T
import os
import re
from .ndi_object import NDI_Object


class EpochSet:
    """ TODO
    """

    def __init__(self, root, epochfiles, metadatafile):
        self.root = root
        self.epochfiles = epochfiles
        self.metadatafile = metadatafile


class FileNavigator(NDI_Object):
    """
    A flatbuffer interface for file_navigators.

    .. currentmodule:: ndi.ndi_object

    Inherits from the :class:`NDI_Object` abstract class.
    """

    def __init__(
        self,
        epoch_file_patterns: T.List[T.RegexStr],
        metadata_file_pattern: T.RegexStr,
        id_: T.NdiId = None
    ) -> None:
        """FileNavigator constructor: initializes with fields defined in `ndi_schema <https://>`_'s FileNavigator table. For use when creating a new FileNavigator instance from scratch.
        ::
            new_file_navigator = FileNavigator(**fields)

        :param epoch_file_patterns: A regex string identifying file names with epoch data.
        :type epoch_file_patterns: str
        :param metadata_file_pattern: A regex string identifying file names containing metadata.
        :type metadata_file_pattern: str
        """
        super().__init__(id_)
        self.add_data_property('epoch_file_patterns', epoch_file_patterns)
        self.add_data_property('metadata_file_pattern', metadata_file_pattern)

    @classmethod
    def from_document(cls, document) -> FileNavigator:
        return cls(
            id_=document.id,
            epoch_file_patterns=document.data['epoch_file_patterns'],
            metadata_file_pattern=document.data['metadata_file_pattern']
        )

    def update(
        self,
        epoch_file_patterns=None,
        metadata_file_pattern=None,
    ) -> None:
        if epoch_file_patterns:
            self.epoch_file_patterns = epoch_file_patterns
        if metadata_file_pattern:
            self.metadata_file_pattern = metadata_file_pattern
        self.ctx.update(self.document, force=True)


    def get_epoch_set(self, directory: T.FilePath):
        """Given a directory, extracts, separates, and stores all files containing epoch or metadata. Files are identified using instance's epoch_file_patterns and metadata_file_pattern.

        :param directory: A path to the data directory.
        :type directory: str
        """
        file_parameters = re.compile('|'.join(self.epoch_file_patterns))
        self.epochs = []
        for root, _, files in os.walk(directory):
            epochfiles = [
                os.path.abspath(os.path.join(root, file))
                for file in files
                if file_parameters.match(file)
            ]
            if epochfiles:
                metadatafile = next(
                    file for file in epochfiles
                    if re.match(self.metadata_file_pattern, file)
                )
                self.epochs.append(EpochSet(root, epochfiles, metadatafile))
                self.epochs.sort(key=lambda epoch: epoch.root)
        return self.epochs
