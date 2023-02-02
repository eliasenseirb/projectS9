import pyaf

class shaping_factory:
    """
    Factory for shaping and matched filters.
    Attributes
    ----------
    payload: int
        payload size in symbols
    rolloff: float
        Rolloff coefficient of the root raised cosine filters (default 0.35)
    oversampling_factor: int
        Number of output samples to be generated per input symbol. (default 2)
    group_delay:
        Group delay of the root raised cosine filters (default 20)
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 payload,
                 rolloff = 0.35,
                 oversampling_factor = 2,
                 group_delay = 20,
                 n_frames = 1):
        """
        Parameters
        ----------
        payload: int
            payload size in symbols
        rolloff: float
            Rolloff coefficient of the root raised cosine filters (default 0.35)
        oversampling_factor: int
            Number of output samples to be generated per input symbol. (default 2)
        group_delay:
            Group delay of the root raised cosine filters (default 20)
        n_frames:
            Number of frames per task execution (default 1)
        """
        self.payload             = payload
        self.rolloff             = rolloff
        self.oversampling_factor = oversampling_factor
        self.group_delay         = group_delay
        self.n_frames            = n_frames

    def build(self):
        """
        Builds a shaping filter and a matched filter from the class attributes.
        """
        h  = pyaf.filter.Filter_root_raised_cosine_ccr.synthetize(self.rolloff,
                                                                  self.oversampling_factor,
                                                                  self.group_delay)

        shaping_filter = pyaf.filter.Filter_UPFIR_ccr(2*self.payload,
                                                      h,
                                                      self.oversampling_factor,
                                                      self.n_frames)

        matched_filter = pyaf.filter.Filter_FIR_ccr  (2*self.payload*self.oversampling_factor,
                                                      h,
                                                      self.n_frames)
        return shaping_filter, matched_filter