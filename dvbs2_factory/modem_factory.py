import os

import py_aff3ct
from py_aff3ct import module as mdl

class modem_factory():
    def __init__(self, N, M, n_frames):
        self.N = N
        self.M  = M
        self.n_frames = n_frames
        # Modulation
        if self.M == 4:
            path_to_cstl = "/conf/mod/4QAM_GRAY.mod"
        elif self.M == 8:
            path_to_cstl = "/conf/mod/8PSK.mod"
        elif self.M == 16:
            path_to_cstl = "/conf/mod/16APSK.mod"
        else:
            path_to_cstl = ""

        if path_to_cstl:
            full_path = os.path.abspath(os.path.dirname(__file__ ) + path_to_cstl)
            self.cstl = py_aff3ct.tools.constellation.Constellation_user(full_path)

    def build(self):
        modem = mdl.modem.Modem_generic_fast(self.N, self.cstl)
        modem.n_frames = self.n_frames
        return modem