import pyaf

class snr_estimator_factory():
    def __init__(self,
                 Ns,
                 R,
                 nb,
                 n_frames = 1):
        self.Ns = Ns
        self.R  = R
        self.nb = nb
        self.n_frames = n_frames

    def build(self):
        snr_estimator = pyaf.estimator.Estimator_DVBS2 (2*self.Ns, self.R, self.nb, self.n_frames)
        return snr_estimator
