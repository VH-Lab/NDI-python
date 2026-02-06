from ..epoch.epochset import Param as EpochSet
from .clocktype import ClockType

class TimeReference:
    def __init__(self, referent, clocktype, epoch, time):
        if not isinstance(referent, EpochSet):
            raise TypeError("referent must be a subclass of ndi.epoch.epochset.Param")

        if not hasattr(referent, 'session') or not hasattr(referent.session, 'id'):
             raise TypeError("The referent must have an ndi.session with a valid id.")

        if not isinstance(clocktype, ClockType):
            raise TypeError("clocktype must be an instance of ndi.time.clocktype.ClockType")

        if clocktype.needsepoch() and not epoch:
            raise ValueError("time is local; an EPOCH must be specified.")

        self.referent = referent
        self.session_ID = referent.session.id()
        self.clocktype = clocktype
        self.epoch = epoch
        self.time = time

    def ndi_timereference_struct(self):
        return {
            'referent_epochsetname': self.referent.epochsetname(),
            'referent_classname': self.referent.__class__.__name__,
            'clocktypestring': str(self.clocktype),
            'epoch': self.epoch,
            'session_ID': self.session_ID,
            'time': self.time
        }
