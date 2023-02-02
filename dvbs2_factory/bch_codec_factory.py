import py_aff3ct
import pyaf

import math
class bch_codec_factory:
    """
    Factory for the BCH encoder and decoder.
    Attributes
    ----------
    K: int
        Number of message bits
    N: int
        Number of codeword bits
    inter: bool
        Flag indicating if an inter frame strategy is used for the BCH encoder (default False).
    GF: py_aff3ct.tools.BCH_polynomial_generator
        AFF3CT tool representing the BCH polynomial generator
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 N,
                 inter = False,
                 n_frames = 1):
        """
        Parameters
        ----------
        N: int
            The number of codeword bits
        inter: bool
            Flag indicating if an inter frame strategy is used for the BCH encoder (default False).
        n_frames:
            The number of frames per task execution (default 1)
        """
        self.N = N # BCH codeword length
        self.K   = self.N - 168 # BCH message length
        self.inter = inter
        N_U = 2**(math.ceil(math.log(self.N, 2)))-1 # BCH raw codeword length (before puncturing)
        self.GF  = py_aff3ct.tools.BCH_polynomial_generator(N_U, 12, [1, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        self.n_frames = n_frames

    def build(self):
        """
        Builds a BCH encoder and a BCH decoder from the class attributes.
        """
        if self.inter:
            bch_encoder = pyaf.encoder.Encoder_BCH_inter_DVBS2 (self.K, self.N, self.GF)
        else:
            bch_encoder = pyaf.encoder.Encoder_BCH_DVBS2 (self.K, self.N, self.GF)
        bch_decoder = pyaf.decoder.Decoder_BCH_DVBS2 (self.K, self.N, self.GF)
        bch_encoder.n_frames = self.n_frames
        bch_decoder.n_frames = self.n_frames
        bch_encoder.name = "BCH_encoder"
        bch_decoder.name = "BCH_decoder"

        return bch_encoder, bch_decoder
