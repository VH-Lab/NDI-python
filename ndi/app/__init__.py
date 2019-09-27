
from ndi.schema.App import App as AppInterface


class App(AppInterface):
    """
    An NDI application which processes information in an experiment or database.

    Derivatives of this class should optionally define an input schema and always define an output schema.
    """
    input_schema = None
    output_schema = None

    def run(self, input):
        """Execute the app inline.

        App definitions should override this method and implement their own input_schema and output_schema static values.
        """
        # No op for the abstract implementation
        pass
