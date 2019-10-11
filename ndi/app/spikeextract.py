from . import App
from scipy.signal import butter, lfilter


class AppSpikeExtract(App):
    """Demo spike extractor."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, probe_data):
        # Hard coded sample frequency while figuring out the interface changes here
        sample_frequency = 30000
        nyquist = sample_frequency / 2
        b, a = butter(2, (500 / nyquist, 9000 / nyquist), btype="bandpass")
        return lfilter(b, a, probe_data)
