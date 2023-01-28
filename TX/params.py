import math

class params:

    def __init__(self, ebn0):
        #self.K = 512
        self.N = 2048
        self.R = 1/2
        self.ebn0 = ebn0
        self.frozen_bits = []
        self.noise = None # temporaire
        self.sec_sz = 0
        self.window_size = 20
        self.Fs = 1e6
        self.Fc = 2.45e9
        self.n_frames =1
        self.MODCOD = "QPSK-S_8/9"
        self.p = 16200

class Bob(params):
    def __init__(self, ebn0):
        self.K=1900
        super().__init__(ebn0)
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))


class Eve(params):
    def __init__(self, ebn0):
        self.K=1500
        super().__init__(ebn0)
        self.ebn0 -= 3
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))