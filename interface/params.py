import math
from myutils import all_no, no, count

class params:

    def __init__(self, ebn0):
        """Common parameters for Bob and Eve"""
        self.K = 3900          # Polar encoder input size
        self.N = 4096          # Polar encoder output size
        self.R = self.K/self.N # Code rate
        self.ebn0 = ebn0
        self.frozen_bits = [] 
        self.noise = None   
        self.seq_pos = []
        self.sec_sz = 0  
        self.window_size = 20  # unused

class Bob(params):
    def __init__(self, ebn0):
        """Specific parameters for Bob"""
        self.frozen_K = 3900
        super().__init__(ebn0)
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))


class Eve(params):
    def __init__(self, ebn0, has_mux=True):
        """Specific parameters for Eve"""
        self.frozen_K = 3500
        super().__init__(ebn0)
        self.ebn0 -= 4
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))
        self.has_mux = has_mux