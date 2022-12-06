import pyaf

class bb_scrambler_factory:
    """
    Factory for the payload scrambler module.

    Attributes
    ----------
    K: int
        message size in bits
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self, K, n_frames):
        """
        Properties
        ----------
        K: int
            message size in bits
        n_frames:
            Number of frames per task execution (default 1)
        """
        self.K = K
        self.n_frames = n_frames

    def build(self):
        """
        Builds a payload scrambler module from the class attributes.
        """
        bb_scrambler = pyaf.scrambler.Scrambler_BB(self.K, self.n_frames)
        return bb_scrambler