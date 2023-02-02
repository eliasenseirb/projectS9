import pyaf

class framer_factory:
    """
    Factory for DVB-S2 Framer module.

    Attributes
    ----------
    Ns: int
        The number of information symbols in a frame
    payload: int
        The payload size (symbols + header + pilots) in symbols
    modcod: std
        The coded modulation name (default "QPSK-S_8/9").
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 Ns,
                 modcod,
                 n_frames = 1):
        """
        Properties
        ----------
        Ns: int
            The number of information symbols in a frame
        modcod: std
            The coded modulation name (default "QPSK-S_8/9").
        n_frames:
            Number of frames per task execution (default 1)
        """
        self.Ns       = Ns
        P             = 36
        N_pilots      = self.Ns // (16 * 90)
        S             = self.Ns // 90
        self.payload  = 90 * (S + 1) + (N_pilots * P)
        self.modcod   = modcod
        self.n_frames = n_frames

    def build(self):
        """
        Builds a DVB-S2 framer from the class attributes.
        """
        framer = pyaf.framer.Framer (2*self.Ns, 2*self.payload, self.modcod, self.n_frames)
        return framer