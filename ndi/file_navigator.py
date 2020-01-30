import os
import re
from .ndi_object import NDI_Object
import ndi.schema.FileNavigator as build_file_navigator


class EpochFiles:
    def __init__(self, epochfiles, metadatafile):
        self.epochfiles = epochfiles
        self.metadatafile = metadatafile


class FileNavigator(NDI_Object):
    def __init__(self, epoch_file_patterns, metadata_file_pattern):
        self.epoch_file_patterns = epoch_file_patterns
        self.metadata_file_pattern = metadata_file_pattern

    @classmethod
    def from_flatbuffer(cls, flatbuffer):
        file_navigator = build_file_navigator.FileNavigator.GetRootAsFileNavigator(
            flatbuffer, 0)
        return cls._reconstruct(file_navigator)

    @classmethod
    def _reconstruct(cls, file_navigator):
        epoch_file_patterns = [
            file_navigator.EpochFilePatterns(i).decode('utf8')
            for i in range(file_navigator.EpochFilePatternsLength())
        ]

        return cls(epoch_file_patterns=epoch_file_patterns,
                   metadata_file_pattern=file_navigator.MetadataFilePattern().decode('utf8'))

    def _build(self, builder):
        epoch_file_patterns = self._buildStringVector(
            builder, self.epoch_file_patterns)
        metadata_file_pattern = builder.CreateString(
            self.metadata_file_pattern)

        build_file_navigator.FileNavigatorStart(builder)
        build_file_navigator.FileNavigatorAddEpochFilePatterns(
            builder, epoch_file_patterns)
        build_file_navigator.FileNavigatorAddMetadataFilePattern(
            builder, metadata_file_pattern)
        return build_file_navigator.FileNavigatorEnd(builder)

    def get_epochs(self, directory):
        file_parameters = re.compile('|'.join(self.epoch_file_patterns))
        self.epochs = []
        for root, _, files in os.walk(directory):
            epochfiles = [
                os.path.abspath(os.path.join(root, file))
                for file in files
                if file_parameters.match(file)
            ]
            if epochfiles:
                metadatafile = [
                    file for file in epochfiles
                    if re.match(self.metadata_file_pattern, file)
                ][0]
                self.epochs.append(EpochFiles(epochfiles, metadatafile))
