from ndi.schema.Probe import Probe as ProbeInterface

class Probe(ProbeInterface):
    """
    An instrument that makes a measurement or provides stimulation. Examples include an electrode, a camera, a 2-photon microscope, a visual stimulus monitor, a nose-poke, a feeder.
    """
    def __init__(self, name, reference):
        self.name = name
        self.reference = reference
