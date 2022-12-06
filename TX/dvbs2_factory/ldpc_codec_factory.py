import py_aff3ct
from py_aff3ct import module as mdl

class ldpc_decoder_params:
    """
    LDPC decoder parameter class.
    Attributes
    ----------
    K: int
        Number of message bits
    N: int
        Number of codeword bits
    H: py_aff3ct.tools.sparse_matrix.array
        AFF3CT tool for representing the parity check matrix
    nb_iterations: int
        The number of decoder iterations
    scheduling: str
        The scheduling type (default = "horizontal_layered").
        Its value should be in the set
          - "flooding"
          - "horizontal_layered"
          - "vertical_layered"
    update_rule: str
        The rule for node update (default is "NMS").
        Its value should be in the set
          - "MS": Min-Sum
          - "NMS": Normalized MS
          - "OMS": Offset MS
          - "SPA": Sum Product Algorithm
          - "LSPA": Linearized SPA
    offset: float
        The offset value used for the OMS update rule (default 0.0).
    normalization: float
        The normalization value used for the NMS update rule (default 1.0).
    enable_syndrome: bool
        Check the syndrome for early decoder exit.
    syndrome_depth: int
        Syndrome depth
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 K,
                 N,
                 H,
                 nb_iterations = 50,
                 scheduling = "horizontal_layered",
                 update_rule = "NMS",
                 offset = 0.0,
                 normalization = 1.0,
                 enable_syndrome = True,
                 syndrome_depth = 1,
                 inter = False,
                 n_frames = 1
                 ):
        self.K               = K
        self.N               = N
        self.H               = H
        self.nb_iterations   = nb_iterations
        self.scheduling      = scheduling
        self.update_rule     = update_rule
        self.offset          = offset
        self.normalization   = normalization
        self.enable_syndrome = enable_syndrome
        self.syndrome_depth  = syndrome_depth
        self.inter           = inter
        self.n_frames        = n_frames

    def build(self, info_bits_pos):

        decoder_class_name = "Decoder_LDPC_BP_" + self.scheduling
        if self.inter:
            decoder_class_name = decoder_class_name + "_inter"
        decoder_class_name = decoder_class_name + "_" + self.update_rule
        if   self.update_rule == "NMS":
            args = (self.K, self.N, self.nb_iterations, self.H, info_bits_pos, self.normalization, self.enable_syndrome, self.syndrome_depth)
        elif self.update_rule == "OMS":
            args = (self.K, self.N, self.nb_iterations, self.H, info_bits_pos, self.off, self.enable_syndrome, self.syndrome_depth)
        elif self.update_rule in ("SPA", "MS", "LSPA"):
            args = (self.K, self.N, self.nb_iterations, self.H, info_bits_pos, self.enable_syndrome, self.syndrome_depth)

        ldpc_decoder = ldpc_decoder = mdl.decoder.__getattribute__(decoder_class_name)(*args)
        ldpc_decoder.n_frames = self.n_frames
        return ldpc_decoder

class ldpc_codec_factory:
    """
    Factory for the LDPC encoder and decoder.
    Attributes
    ----------
    K: int
        Number of message bits
    N: int
        Number of codeword bits
    encoder_params: py_aff3ct.tools.dvbs2_values.dvbs2_values
        AFF3CT tool building the DVBS2 LDPC encoder
    decoder_params: ldpc_decoder_params
        LDPC decoder parameter class
    H: py_aff3ct.tools.sparse_matrix.array
        AFF3CT tool for representing the parity check matrix
    n_frames:
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 K,
                 N,
                 n_frames = 1):
        """
        Parameters
        ----------
        K: int
            The number of uncoded message bits
        N: int
            The number of codeword bits
        n_frames:
            The number of frames per task execution (default 1)
        """
        self.K = K
        self.N = N
        self.encoder_params = py_aff3ct.tools.dvbs2_values.__getattribute__("dvbs2_values_" + str(self.N) + "_" + str(self.N-self.K))()
        self.H = self.encoder_params.build_H()
        self.n_frames = n_frames
        self.decoder_params = ldpc_decoder_params(self.K,self.N,self.H, n_frames = self.n_frames)

    def build(self):
        """
        Builds a LDPC encoder and a LDPC decoder from the class attributes.
        """
        # LDPC
        ldpc_encoder = mdl.encoder.Encoder_LDPC_DVBS2(self.encoder_params)
        ldpc_encoder.n_frames = self.n_frames
        ldpc_decoder = self.decoder_params.build(ldpc_encoder.get_info_bits_pos())
        return ldpc_encoder, ldpc_decoder

if __name__ == "__main__":
    ldpc_factory = ldpc_codec_factory(6480,16200)
    ldpc_factory.decoder_params.scheduling = "flooding"
    ldpc_factory.decoder_params.update_rule = "SPA"
    encoder, decoder = ldpc_factory.build()
    encoder.name = "LDPC_encoder"
    print(type(decoder))

