class System:
    def __init__(self, name, filenavigator, daqreader, daqmetadatareader=None):
        self.name = name
        self.filenavigator = filenavigator
        self.daqreader = daqreader
        self.daqmetadatareader = daqmetadatareader if daqmetadatareader is not None else []

    def set_daqmetadatareader(self, thedaqmetadatareaders):
        pass

    def __eq__(self, other):
        if not isinstance(other, System):
            return NotImplemented
        return self.name == other.name and self.__class__ == other.__class__

    def epochclock(self, epoch_number):
        pass

    def t0_t1(self, epoch_number):
        pass

    def epochid(self, epoch_number):
        pass

    def getprobes(self):
        pass

    def session(self):
        pass

    def setsession(self, session):
        pass

    def deleteepoch(self, number, removedata):
        pass

    def getcache(self):
        pass

    def buildepochtable(self):
        pass

    def epochprobemapfilename(self, epochnumber):
        pass

    def verifyepochprobemap(self, epochprobemap, epoch):
        pass

    def epochtagfilename(self, epochnumber):
        pass

    def getepochprobemap(self, epoch, filenaveepochprobemap):
        pass

    def getmetadata(self, epoch, channel):
        pass

    def ingest(self):
        pass

    def newdocument(self):
        pass

    def searchquery(self):
        pass
