import math

class params:

    def __init__(self, ebn0):
        self.K = 512
        self.N = 1024
        self.R = 1/2
        self.ebn0 = ebn0
        self.frozen_bits = []
        self.noise = None # temporaire
        params.sec_sz = 0

class Bob(params):
    def __init__(self, ebn0):
        super().__init__(ebn0)
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))


class Eve(params):
    def __init__(self, ebn0):
        super().__init__(ebn0)
        self.ebn0 -= 12
        self.esn0 = self.ebn0 + 10*math.log10(self.K/self.N)
        self.sigma = 1/(math.sqrt(2)*10**(self.esn0/20))