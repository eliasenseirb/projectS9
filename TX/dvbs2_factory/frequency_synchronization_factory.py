import pyaf

import math

class coarse_frequency_synchronization_params:
    """
    Class for handling coarse frequency synchronization parameters.
    Attributes
    ----------
    damping: float
        damping factor of the coarse synchonization pilot aided phase locked loop (default math.sqrt(0.5))
    normalized_bandwidth: float
        normalized bandwidth of the coarse synchonization pilot aided phase locked loop (default 1e-4)
    """
    def __init__(self,
                 damping              = math.sqrt(0.5),
                 normalized_bandwidth = 1e-4,):
        self.damping              = damping
        self.normalized_bandwidth = normalized_bandwidth
    """
    Parameters
    ----------
    damping: float
        damping factor of the coarse synchonization pilot aided phase locked loop (default math.sqrt(0.5))
    normalized_bandwidth: float
        normalized bandwidth of the coarse synchonization pilot aided phase locked loop (default 1e-4)
    """

class luise_reggiannini_frequency_synchronization_params:
    """
    Class for handling Luise and Reggiannini frequency synchronization parameters.
    Attributes
    ----------
    damping: float
        damping factor for averaging LR output over several frames (default 0.999)
    """
    def __init__(self, damping = 0.999):
        """
        Parameters
        ----------
        damping: float
            damping factor for averaging LR output over several frames (default 0.999)
        """
        self.damping = damping

class frequency_synchronization_factory:
    """
    Factory for frequency synchornization modules.
    Attributes
    ----------
    payload: int
        payload size in symbols
    oversampling_factor: int
        Number of output samples to be generated per input symbol. (default 2)
    coarse_params: coarse_frequency_synchronization_params
        Parameters for building the coarse frequency synchronization module
    lr_params:
        Parameters for building the Luise and Reggiannini synchronization module
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 payload,
                 oversampling_factor = 2,
                 n_frames = 1):
        """
        Parameters
        ----------
        payload: int
            payload size in symbols
        oversampling_factor: int
            Number of output samples to be generated per input symbol. (default 2)
        n_frames:
            Number of frames per task execution (default 1)
        """
        self.payload             = payload
        self.oversampling_factor = oversampling_factor
        self.coarse_params       = coarse_frequency_synchronization_params()
        self.lr_params           = luise_reggiannini_frequency_synchronization_params()
        self.n_frames            = n_frames

    def build(self):
        """
        From the class attributes, builds:
         - a coarse frequency synchronization module,
         - a Luise and Reggianini frequency synchronization module,
         - a fine frequency and phase recovery module
        """
        coarse_frq_sync = pyaf.synchronizer.frequency.Synchronizer_freq_coarse_DVBS2      (2*self.payload*self.oversampling_factor, self.oversampling_factor, self.coarse_params.damping, self.coarse_params.normalized_bandwidth, self.n_frames)
        lr_frq_sync     = pyaf.synchronizer.frequency.Synchronizer_Luise_Reggiannini_DVBS2(2*self.payload, self.lr_params.damping, self.n_frames)
        fp_frq_sync     = pyaf.synchronizer.frequency.Synchronizer_freq_phase_DVBS2       (2*self.payload, self.n_frames)
        coarse_frq_sync.name = "co_frq_sync"
        fp_frq_sync.name     = "fp_frq_sync"
        lr_frq_sync.name     = "lr_frq_sync"
        return coarse_frq_sync, lr_frq_sync, fp_frq_sync
