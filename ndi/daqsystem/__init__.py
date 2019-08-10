from ndi.schema.DaqSystem import DaqSystem as DaqSystemInterface


class DaqSystem(DaqSystemInterface):
    """
    This class represents an abstract DaqSystem which implementions should extend.
    """

    def __init__(self, name, daq_reader):
        self.name = name
        self.daq_reader = daq_reader
