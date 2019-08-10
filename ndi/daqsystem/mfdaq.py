from . import DaqSystem
from .daqreader import DaqReader


class DaqSystemMultiFunction(DaqSystem):
    """This object allows one to address multifunction data acquisition systems that sample a variety of data types potentially simultaneously. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DaqReaderMultiFunction(DaqReader):
    """This object allows one to address multifunction data acquisition systems that sample a variety of data types potentially simultaneously. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
