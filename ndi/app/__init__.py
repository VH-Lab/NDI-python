
from ndi.schema import App as AppInterface


class App(AppInterface):
    """
    An NDI application which processes information in an experiment or database.

    Derivatives of this class should optionally define an input schema and always define an output schema.
    """
    input_schema = None
    output_schema = None
    def __init__(self):
        pass