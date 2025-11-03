from . import Timeseries

class Mfdaq(Timeseries):
    def __init__(self, session, name, reference, type_, subject_id):
        super().__init__(session, name, reference, type_, subject_id)

    def read_epochsamples(self, epoch, s0, s1):
        # implementation will go here
        pass

    def readtimeseriesepoch(self, epoch, t0, t1):
        # implementation will go here
        pass

    def samplerate(self, epoch):
        # implementation will go here
        pass

    def readtimeseries(self, timeref_or_epoch, t0, t1):
        # This is the abstract method from the parent class
        # implementation will go here
        pass
