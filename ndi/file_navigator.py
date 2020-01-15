import os
import re

class EpochFiles:
    def __init__(self, epochfiles, metadatafile):
        self.epochfiles = epochfiles
        self.metadatafile = metadatafile

class FileNavigator:
    def __init__(self, directory, epochfilepatterns, metadata_pattern):
        self.fileparameters = re.compile('|'.join(epochfilepatterns))
        self.epochs = []
        for root, _, files in os.walk(directory):
            epochfiles = [
                os.path.abspath(os.path.join(root, file))
                for file in files
                if self.fileparameters.match(file)
            ]
            if epochfiles:
                metadatafile = [
                    file for file in epochfiles
                    if re.match(metadata_pattern, file)
                ][0]
                self.epochs.append(EpochFiles(epochfiles, metadatafile))
