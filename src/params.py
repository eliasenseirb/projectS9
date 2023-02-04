import math
from frozenbits_handler import all_no, no, count

class params:

    def __init__(self, ebn0):
        """Common parameters for Bob and Eve"""
        self.K = 900
        self.N = 1024
        self.R = self.K/self.N
        self.ebn0 = ebn0
        self.frozen_bits = []
        self.noise = None # temporaire
        self.seq_pos = []
        self.sec_sz = 0
        self.window_size = 20

class Bob(params):
    def __init__(self, ebn0):
        """Specific parameters for Bob"""
        self.K = 900
        super().__init__(ebn0)
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))


class Eve(params):
    def __init__(self, ebn0, has_mux=False):
        """Specific parameters for Eve"""
        self.K = 500
        super().__init__(ebn0)
        self.ebn0 -= 3
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))
        self.has_mux = has_mux