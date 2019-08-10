class DaqReader():
    """A reader associated with a DaqSystem."""
    # TODO - This should probably have an abstract type as well?

    def __init__(self, path):
        self.path = path
