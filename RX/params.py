import math

class params:

    def __init__(self, ebn0):
        """Common parameters for Bob and Eve"""
        self.K = 1900
        self.N = 2048              # Polar encoder output size
        self.R = self.K/self.N     # Rate of the code
        self.ebn0 = ebn0           # SNR
        self.frozen_bits = []   
        self.noise = None
        self.sec_sz = 0            # number of secrecy bits
        self.window_size = 20      # unused
        self.Fs = 1e6              # Sampling frequency
        self.Fc = 868e6            # carrier frequency
        self.n_frames =1           # number of frames
        self.MODCOD = "QPSK-S_8/9" # modulation
        self.p = 16200             # padding size 
        self.freq_shift = 0.025

class Bob(params):
    def __init__(self, ebn0):
        """Specific parameters for Bob"""
        self.frozen_K = 1900
        super().__init__(ebn0)
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))


class Eve(params):
    def __init__(self, ebn0):
        """Specific parameters for Eve"""
        self.frozen_K = 1500
        super().__init__(ebn0)
        self.ebn0 -= 3
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))
