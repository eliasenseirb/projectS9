import pyaf

import math

class timing_synchronization_factory:
    """
    Factory for timing recovery device.
    Timing synchronization relies on the Gardner algorithm.

    Attributes
    ----------
    payload: int
        payload size in symbols
    oversampling_factor: int
        Number of output samples to be generated per input symbol. (default 2)
    damping: float
        The Damping factor of the Gardner's loop filter (default 1/math.sqrt(2))
    normalized_bandwidth: float
        The normalized bandwidth of the Gardner's loop filter (default 5e-5)
    detector_gain: float
        The detector gain of the Gardner's loop filter (default 2.0)
    fast: bool
        Flag indicating if a fast implementation should be used (default True)
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 payload,
                 oversampling_factor  = 2,
                 damping              = math.sqrt(0.5),
                 normalized_bandwidth = 5e-5,
                 detector_gain        = 2.0,
                 fast                 = True,
                 n_frames             = 1):
        """
        Parameters
        ----------
        payload: int
            payload size in symbols
        oversampling_factor: int
            Number of output samples to be generated per input symbol. (default 2)
        damping: float
            The Damping factor of the Gardner's loop filter (default 1/math.sqrt(2))
        normalized_bandwidth: float
            The normalized bandwidth of the Gardner's loop filter (default 5e-5)
        detector_gain: float
            The detector gain of the Gardner's loop filter (default 2.0)
        fast: bool
            Flag indicating if a fast implementation should be used (default True)
        n_frames:
            Number of frames per task execution (default 1)
        """
        self.payload              = payload
        self.oversampling_factor  = oversampling_factor
        self.damping              = damping
        self.normalized_bandwidth = normalized_bandwidth
        self.detector_gain        = detector_gain
        self.fast                 = fast
        self.n_frames             = n_frames

    def build(self):
        """
        Builds a timing synchronization module from the class attributes.
        """
        if self.oversampling_factor == 2:
            if self.fast:
                timing_sync = pyaf.synchronizer.timing.Synchronizer_Gardner_fast_osf2(2*self.payload*self.oversampling_factor,
                                                                               self.damping,
                                                                               self.normalized_bandwidth,
                                                                               self.detector_gain,
                                                                               self.n_frames)
            else:
                timing_sync = pyaf.synchronizer.timing.Synchronizer_Gardner(2*self.payload*self.oversampling_factor,
                                                                     self.oversampling_factor,
                                                                     self.damping,
                                                                     self.normalized_bandwidth,
                                                                     self.detector_gain,
                                                                     self.n_frames)
        else:
            if self.fast:
                timing_sync = pyaf.synchronizer.timing.Synchronizer_Gardner_fast(2*self.payload*self.oversampling_factor,
                                                                          self.oversampling_factor,
                                                                          self.damping,
                                                                          self.normalized_bandwidth,
                                                                          self.detector_gain,
                                                                          self.n_frames)
            else:
                timing_sync = pyaf.synchronizer.timing.Synchronizer_Gardner(2*self.payload*self.oversampling_factor,
                                                                     self.oversampling_factor,
                                                                     self.damping,
                                                                     self.normalized_bandwidth,
                                                                     self.detector_gain,
                                                                     self.n_frames)
        timing_sync.name = "timing_sync"
        return timing_sync
