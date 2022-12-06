import pyaf

class pl_scrambler_factory:
    """
    Factory for the payload scrambler module.

    Attributes
    ----------
    payload: int
        payload size in symbols
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self, payload, n_frames):
        """
        Properties
        ----------
        payload: int
            payload size in symbols
        n_frames:
            Number of frames per task execution (default 1)
        """
        self.payload = payload
        self.n_frames = n_frames

    def build(self):
        """
        Builds a payload scrambler module from the class attributes.
        """
        pl_scrambler = pyaf.scrambler.Scrambler_PL(2*self.payload, 90, self.n_frames)
        return pl_scrambler