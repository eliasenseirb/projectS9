import sys
import os
pyaf_path = os.path.abspath(os.path.dirname(__file__ ) + '/../../build/lib')
sys.path.insert(0, pyaf_path) # pyaf location
py_aff3ct_path = os.path.abspath(os.path.dirname(__file__ ) + '/../../py_aff3ct/build/lib')
sys.path.insert(0, py_aff3ct_path) # py_aff3ct location

from .bb_scrambler_factory import bb_scrambler_factory
from .bch_codec_factory import bch_codec_factory
from .frame_synchronization_factory import frame_synchronization_factory
from .framer_factory import framer_factory
from .frequency_synchronization_factory import frequency_synchronization_factory
from .ldpc_codec_factory import ldpc_codec_factory
from .modem_factory import modem_factory
from .pl_scrambler_factory import pl_scrambler_factory
from .shaping_factory import shaping_factory
from .snr_estimator_factory import snr_estimator_factory
from .source_factory import source_factory
from .symbol_agc_factory import symbol_agc_factory
from .timing_synchronization_factory import timing_synchronization_factory

import math

class dvbs2_factory():
    def __init__(self,
                 modcod   = "QPSK-S_8/9",
                 osf      = 2,
                 file_path = '',
                 n_frames = 1):

        if modcod == "QPSK-S_8/9":
            R_LDPC  = 8/9
            M       = 4
            N_LDPC  = 16200
        elif modcod == "QPSK-S_3/5":
            R_LDPC  = 3/5
            M       = 4
            N_LDPC  = 16200
        elif modcod == "8PSK-S_3/5":
            R_LDPC  = 3/5
            M       = 8
            N_LDPC  = 16200
            read_order = "TOP_RIGHT"
        elif modcod == "8PSK-S_8/9":
            R_LDPC  = 8/9
            M       = 8
            N_LDPC  = 16200
            read_order = "TOP_LEFT"
        elif modcod == "16APSK-S_8/9":
            R_LDPC  = 8/9
            M       = 16
            N_LDPC  = 16200
            read_order = "TOP_LEFT"
        else:
            raise Exception("Unhandled 'modcod' type.")

        nb      = math.floor(math.log(M, 2))           # Number of bits per symbol
        Ns      = N_LDPC//nb
        N_BCH   = math.floor(N_LDPC * R_LDPC)     # BCH message length
        K_BCH   = N_BCH - 168                          # BCH codeword length
        N_BCH_U = 2**(math.ceil(math.log(N_BCH, 2)))-1 # BCH raw codeword length (before puncturing)
        K_LDPC  = N_BCH

        self.bch_codec_f                 = bch_codec_factory                (N_BCH,                            n_frames = n_frames)
        self.bb_scrambler_f              = bb_scrambler_factory             (self.bch_codec_f.K,               n_frames = n_frames)
        self.source_f                    = source_factory                   (self.bch_codec_f.K, file_path= file_path              ,n_frames = n_frames)
        self.ldpc_codec_f                = ldpc_codec_factory               (K_LDPC, N_LDPC,                   n_frames = n_frames)
        self.modem_f                     = modem_factory                    (N_LDPC, M,                        n_frames = n_frames)
        self.framer_f                    = framer_factory                   (Ns, modcod,                       n_frames = n_frames)
        payload = self.framer_f.payload
        self.pl_scrambler_f              = pl_scrambler_factory             (payload,                          n_frames = n_frames)
        self.shaping_f                   = shaping_factory                  (payload, oversampling_factor=osf, n_frames = n_frames)
        self.frame_synchronization_f     = frame_synchronization_factory    (payload,                          n_frames = n_frames)
        self.frequency_synchronization_f = frequency_synchronization_factory(payload, oversampling_factor=osf, n_frames = n_frames)
        self.snr_estimator_f             = snr_estimator_factory            (Ns, R_LDPC,nb,                    n_frames = n_frames)
        self.symbol_agc_f                = symbol_agc_factory               (payload,                          n_frames = n_frames)
        self.timing_synchronization_f    = timing_synchronization_factory   (payload, oversampling_factor=osf, n_frames = n_frames)
