"""

Setup the radio

"""

from dvbs2_factory import dvbs2_factory
import py_aff3ct
from py_aff3ct import module as mdl
import pyaf

class Radio():
    """Config for radio"""

    def __init__(self, params, file_path):
        self.params = params
        self.file_path = file_path
        self.dvs2_factory = dvbs2_factory(params.MODCOD, n_frames=params.n_frames)
        self.rad_params = pyaf.radio.USRP_params()
        self.setup()

    def setup(self):
        self._setup_dvs2()
        self._build()
        self._setup_channel()
        self._setup_rad_params()

    def _setup_dvs2(self):
        
        self.dvs2_factory.ldpc_codec_f.decoder_params.inter = True
        self.dvs2_factory.bch_codec_f.inter = True
        self.dvs2_factory.timing_synchronization_f.detector_gain = 2.7
        self.dvs2_factory.timing_synchronization_f.damping = 1
        self.dvs2_factory.timing_synchronization_f.normalized_bandwidth = 0.01

    def _setup_channel(self):
        # Build the channel
        self.N_chn_spls = 2*self.dvs2_factory.shaping_f.payload * self.dvs2_factory.shaping_f.oversampling_factor
        
        self.freq_shift         = pyaf.multiplier.Multiplier_sine_ccc(self.N_chn_spls, self.params.freq_shift, n_frames = self.params.n_frames)
        self.gaussian_noise_gen = py_aff3ct.tools.Gaussian_noise_generator_implem.FAST
        self.awgn               = mdl.channel.Channel_AWGN_LLR(self.N_chn_spls, self.gaussian_noise_gen)
        self.awgn.n_frames      = self.params.n_frames

    def _setup_rad_params(self):
        self.rad_params.fifo_size  = 100
        self.rad_params.N          = self.N_chn_spls//2
        self.rad_params.threaded   = True
        self.rad_params.rx_enabled = True
        self.rad_params.usrp_addr  = "type=b100"
        self.rad_params.rx_rate    = self.params.Fs
        self.rad_params.rx_antenna = "TX/RX"
        self.rad_params.rx_freq    = self.params.Fc
        self.rad_params.rx_gain    = 10

    @property
    def modules(self):
        
        return [self.source,
                self.bb_scrambler,
                self.bch_encoder, bch_decoder,
                self.ldpc_encoder, ldpc_decoder,
                self.modem,
                self.framer,
                self.pl_scrambler,
                self.shp_filter, mcd_filter,
                self.coarse_frq_sync, lr_frq_sync, fp_frq_sync,
                self.timing_sync,
                self.symbol_agc,
                self.frame_sync,
                self.noise_est]

    def _build(self):
        # Build the TX and RX modules
        self.modem                                     = self.dvs2_factory.modem_f                    .build()
        self.framer                                    = self.dvs2_factory.framer_f                   .build()
        self.pl_scrambler                              = self.dvs2_factory.pl_scrambler_f             .build()
        self.shp_filter, mcd_filter                    = self.dvs2_factory.shaping_f                  .build()
        self.coarse_frq_sync, lr_frq_sync, fp_frq_sync = self.dvs2_factory.frequency_synchronization_f.build()
        self.timing_sync                               = self.dvs2_factory.timing_synchronization_f   .build()
        self.symbol_agc                                = self.dvs2_factory.symbol_agc_f               .build()
        self.frame_sync                                = self.dvs2_factory.frame_synchronization_f    .build()
        self.noise_est                                 = self.dvs2_factory.snr_estimator_f            .build()