import pyaf

class symbol_agc_factory:
    """
    Factory for symbol Automatic Gain Control module.

    Attributes
    ----------
    payload: int
        payload size in symbols
    output_energy: float
        Output energy per complex symbol (default 1.0)
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 payload,
                 output_energy = 1.0,
                 n_frames = 1):
        """
        Properties
        ----------
        payload: int
            payload size in symbols
        output_energy: float
            Output energy per complex symbol (default 1.0)
        n_frames:
            Number of frames per task execution (default 1)
        """
        self.payload = payload
        self.output_energy = output_energy
        self.n_frames = n_frames

    def build(self):
        """
        Builds a symbol AGC from the class attributes.
        """
        symbol_AGC = pyaf.multiplier.Multiplier_AGC_cc (2*self.payload, self.output_energy, self.n_frames)
        return symbol_AGC