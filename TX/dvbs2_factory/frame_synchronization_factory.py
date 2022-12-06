import pyaf

class frame_synchronization_factory:
    """
    Factory for the frame synchronization module.

    Attributes
    ----------
    payload: int
        payload size in symbols
    damping: float
        The Damping factor for averaging past results (default 0.7)
    trigger: float
        Threshold for detecting a frame (default 25)
    fast: bool
        Flag indicating if a fast implementation should be used (default True)
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 payload,
                 damping = 0.7,
                 trigger = 25.0,
                 fast = True,
                 n_frames = 1):
        """
        Parameters
        ----------
        payload: int
            payload size in symbols
        damping: float
            The Damping factor for averaging past results (default 0.7)
        trigger: float
            Threshold for detecting a frame (default 25)
        fast: bool
            Flag indicating if a fast implementation should be used (default True)
        n_frames:
            Number of frames per task execution (default 1)
        """
        self.payload = payload
        self.damping = damping
        self.trigger = trigger
        self.fast = fast
        self.n_frames = n_frames

    def build(self):
        """
        Builds a frame synchronization module from the class attributes.
        """
        if self.fast:
            frame_sync = pyaf.synchronizer.frame.Synchronizer_frame_DVBS2_fast(2*self.payload, self.damping, self.trigger,self.n_frames)
        else:
            frame_sync = pyaf.synchronizer.frame.Synchronizer_frame_DVBS2_aib(2*self.payload, self.damping, self.trigger,self.n_frames)
        frame_sync.name =  "frame_sync"
        return frame_sync

