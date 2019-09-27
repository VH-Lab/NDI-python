from . import App


class AppSpikeExtract(App):
    """Demo spike extractor."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_spikewaves_epoch(self):
        # TODO - Return some real values!
        return []
