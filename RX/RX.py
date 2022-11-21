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
Fs=1e6
Fc=868e6

dvs2_factory = dvbs2_factory(MODCOD, n_frames=n_frames)
dvs2_factory.ldpc_codec_f.decoder_params.inter = True
dvs2_factory.bch_codec_f.inter = True
dvs2_factory.timing_synchronization_f.detector_gain = 2.7
dvs2_factory.timing_synchronization_f.damping = 1
dvs2_factory.timing_synchronization_f.normalized_bandwidth = 0.01

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

# Build the channel
N_chn_spls = 2*dvs2_factory.shaping_f.payload * dvs2_factory.shaping_f.oversampling_factor
freq_shift                                = pyaf.multiplier.Multiplier_sine_ccc(N_chn_spls, freq_shift, n_frames = n_frames)
gaussian_noise_gen                        = py_aff3ct.tools.Gaussian_noise_generator_implem.FAST
awgn                                      = mdl.channel.Channel_AWGN_LLR(N_chn_spls, gaussian_noise_gen)
awgn.n_frames = n_frames

sigma_array = sigma * np.ones(shape = (n_frames,1),  dtype = np.float32)
awgn["add_noise::CP"] = sigma_array

rad_params = pyaf.radio.USRP_params()
rad_params.fifo_size  = 100
rad_params.N          = N_chn_spls//2
rad_params.threaded   = True
rad_params.rx_enabled = True
rad_params.usrp_addr  = "type=b100"
rad_params.rx_rate    = Fs
rad_params.rx_antenna = "TX/RX"
rad_params.rx_freq    = Fc
rad_params.rx_gain    = 10

rad      = pyaf.radio.Radio_USRP(rad_params)

rad.n_frames=n_frames

coarse_frq_sync ["synchronize::X_N1"] = rad["receive::Y_N1"] 
coarse_frq_sync ["synchronize::Y_N2"] = mcd_filter      [     "filter::X_N1"]
mcd_filter      [     "filter::Y_N2"] = timing_sync     ["synchronize::X_N1"]
timing_sync     [    "extract::Y_N1"] = timing_sync     ["synchronize::Y_N1"]
timing_sync     [    "extract::B_N1"] = timing_sync     ["synchronize::B_N1"]
symbol_agc      [  "imultiply::X_N" ] = timing_sync     [    "extract::Y_N2"]
symbol_agc      [  "imultiply::Z_N" ] = frame_sync      ["synchronize::X_N1"]
pl_scrambler    [ "descramble::Y_N1"] = frame_sync      ["synchronize::Y_N2"]
lr_frq_sync     ["synchronize::X_N1"] = pl_scrambler    [ "descramble::Y_N2"]
fp_frq_sync     ["synchronize::X_N1"] = lr_frq_sync     ["synchronize::Y_N2"]
framer          [ "remove_plh::Y_N1"] = fp_frq_sync     ["synchronize::Y_N2"]
framer          [ "remove_plh::Y_N2"] = noise_est       [   "estimate::X_N" ]
modem           [ "demodulate::CP"  ] = noise_est       [   "estimate::SIG" ]
modem           [ "demodulate::Y_N1"] = framer          [ "remove_plh::Y_N2"]
ldpc_decoder    ["decode_siho::Y_N" ] = modem           [ "demodulate::Y_N2"]
ldpc_decoder    ["decode_siho::V_K" ] = bch_decoder     ["decode_hiho::Y_N" ]
bb_scrambler    [ "descramble::Y_N1"] = bch_decoder     ["decode_hiho::V_K" ]

sequence = threaded_sequence(rad["receive"]) # py_aff3ct.tools.sequence.Sequence
print(bb_scrambler    [ "descramble::Y_N1"][:])


for lt in sequence.get_tasks_per_types():
    for t in lt:
        t.stats = True
        #t.debug = True
        #t.set_debug_precision(8)
        #t.set_debug_limit(10)

plt.figure()
plt.subplot(121)
rx_cstl = sck_plot(rad["receive::Y_N1"][0,0::2], rad["receive::Y_N1"][0,1::2],'.')
plt.xlim((-4, 4))
plt.ylim((-4, 4))
plt.grid()

plt.subplot(122)
tim_plt = sck_plot(fp_frq_sync     ["synchronize::Y_N2"][0,0::2], fp_frq_sync     ["synchronize::Y_N2"][0,1::2],'.')
tim_plt.line.axes.set_xlim(-4, 4)
tim_plt.line.axes.set_ylim(-4, 4)
plt.grid()

sequence.start()
initial_time = time.time()
while sequence.is_alive():
    starting_time = time.time()
    rx_cstl.refresh()
    tim_plt.refresh()
    pause_time = 1/frame_rate - time.time() + starting_time
    plt.pause(pause_time)

sequence.show_stats()