from signal import pause
import sys
sys.path.insert(0, '../build/lib') # pyaf location
sys.path.insert(0, '../py_aff3ct/build/lib') # py_aff3ct location
sys.path.insert(0, '../src/python') # place of some useful python classes
from py_aff3ct import module as mdl
import pyaf
import py_aff3ct
from dvbs2_factory import dvbs2_factory
from threaded_sequence import threaded_sequence
from sck_plot import sck_plot
from sck_waterfall import sck_waterfall
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import time
import math

MODCOD     = "QPSK-S_8/9"
n_frames   = 8
frame_rate = 25
freq_shift = 0.025
Es_N0_dB   = 10
file_path = "/home/guillaume/Images/oeil.jpg"

dvs2_factory = dvbs2_factory(MODCOD, n_frames=n_frames, file_path=file_path)
dvs2_factory.ldpc_codec_f.decoder_params.inter = True
dvs2_factory.bch_codec_f.inter = True

Es_N0      = 10**(Es_N0_dB/10)
sigma      = 1/math.sqrt(2*Es_N0)

# Build the TX and RX modules
source                                    = dvs2_factory.source_f                   .build()
bb_scrambler                              = dvs2_factory.bb_scrambler_f             .build()
bch_encoder, bch_decoder                  = dvs2_factory.bch_codec_f                .build()
ldpc_encoder, ldpc_decoder                = dvs2_factory.ldpc_codec_f               .build()
modem                                     = dvs2_factory.modem_f                    .build()
framer                                    = dvs2_factory.framer_f                   .build()
pl_scrambler                              = dvs2_factory.pl_scrambler_f             .build()
shp_filter, mcd_filter                    = dvs2_factory.shaping_f                  .build()
coarse_frq_sync, lr_frq_sync, fp_frq_sync = dvs2_factory.frequency_synchronization_f.build()
timing_sync                               = dvs2_factory.timing_synchronization_f   .build()
symbol_agc                                = dvs2_factory.symbol_agc_f               .build()
frame_sync                                = dvs2_factory.frame_synchronization_f    .build()
noise_est                                 = dvs2_factory.snr_estimator_f            .build()
Fs = 1e6
Fc = 868e6


# Build the channel
N_chn_spls = 2*dvs2_factory.shaping_f.payload * dvs2_factory.shaping_f.oversampling_factor
freq_shift                                = pyaf.multiplier.Multiplier_sine_ccc(N_chn_spls, freq_shift, n_frames = n_frames)
gaussian_noise_gen                        = py_aff3ct.tools.Gaussian_noise_generator_implem.FAST
awgn                                      = mdl.channel.Channel_AWGN_LLR(N_chn_spls, gaussian_noise_gen)
awgn.n_frames = n_frames

g = 0.25
v = np.zeros((N_chn_spls,))
v[0::2] = g
gain = pyaf.multiplier.Multiplier_sequence_ccc(N_chn_spls,v,n_frames)


# Build radio
rad_params = pyaf.radio.USRP_params()
rad_params.fifo_size  = 100
rad_params.N          = N_chn_spls//2 
rad_params.threaded   = True
rad_params.tx_enabled = True
rad_params.usrp_addr  = "type=b100"
rad_params.tx_rate    = Fs
rad_params.tx_antenna = "TX/RX"
rad_params.tx_freq    = Fc
rad_params.tx_gain    = 10

rad      = pyaf.radio.Radio_USRP(rad_params)
rad.n_frames = 8

source          [   "generate::U_K" ] = bb_scrambler    [   "scramble::X_N1"]
bb_scrambler    [   "scramble::X_N2"] = bch_encoder     [     "encode::U_K" ]
bch_encoder     [     "encode::X_N" ] = ldpc_encoder    [     "encode::U_K" ]
ldpc_encoder    [     "encode::X_N" ] = modem           [   "modulate::X_N1"]
framer          [   "generate::Y_N1"] = modem           [   "modulate::X_N2"]
framer          [   "generate::Y_N2"] = pl_scrambler    [   "scramble::X_N1"]
shp_filter      [     "filter::X_N1"] = pl_scrambler    [   "scramble::X_N2"]

# shp_filter      ["filter"].info()
# rad      ["send"].info()
shp_filter      [     "filter::Y_N2"] = gain["imultiply::X_N"]
rad             [       "send::X_N1"] = gain["imultiply::Z_N"]


sequence = threaded_sequence(source["generate"]) # py_aff3ct.tools.sequence.Sequence
sequence.export_dot("test.dot")
for lt in sequence.get_tasks_per_types():
    for t in lt:
        t.stats = True
        #t.debug = True
        #t.set_debug_precision(8)
        #t.set_debug_limit(10)


sequence.start()
initial_time = time.time()
while sequence.is_alive():
    pass

sequence.show_stats()