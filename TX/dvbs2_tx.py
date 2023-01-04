from dotenv import load_dotenv
import os
import sys

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
import py_aff3ct as aff3ct

sys.path.append(os.getenv("PYAF_PATH"))
import pyaf

sys.path.append(os.getenv("THREADED_PATH"))
import threaded_sequence


from dvbs2_factory import dvbs2_factory
from signal import pause
from threaded_sequence import threaded_sequence
import numpy as np
import time
import matplotlib.pyplot as plt
from Modules.Mod_MUX import py_MUX 
from Modules.padder import Padder


MODCOD     = "QPSK-S_8/9"
n_frames   = 1
path = "./text.txt"
Fs = 8e6
Fc = 868e6

dvs2_factory = dvbs2_factory(MODCOD,file_path= path, n_frames=n_frames)
dvs2_factory.ldpc_codec_f.decoder_params.inter = True
dvs2_factory.bch_codec_f.inter = True



# Build the TX modules
source                                    = dvs2_factory.source_f                   .build()
bb_scrambler                              = dvs2_factory.bb_scrambler_f             .build()
bch_encoder, bch_decoder                  = dvs2_factory.bch_codec_f                .build()
ldpc_encoder, ldpc_decoder                = dvs2_factory.ldpc_codec_f               .build()
modem                                     = dvs2_factory.modem_f                    .build()
framer                                    = dvs2_factory.framer_f                   .build()
pl_scrambler                              = dvs2_factory.pl_scrambler_f             .build()
shp_filter, mcd_filter                    = dvs2_factory.shaping_f                  .build()


N_chn_spls = 2*dvs2_factory.shaping_f.payload * dvs2_factory.shaping_f.oversampling_factor

g = 0.25
v = np.zeros((N_chn_spls,))
v[0::2] = g
gain = pyaf.multiplier.Multiplier_sequence_ccc(N_chn_spls,v,n_frames)


# Build radio
rad_params = pyaf.radio.USRP_params()
rad_params.fifo_size  = 100
rad_params.N          = 33480//2 
rad_params.threaded   = True
rad_params.tx_enabled = True
rad_params.usrp_addr  = "type=b100"
rad_params.tx_rate    = Fs
rad_params.tx_antenna = "TX/RX"
rad_params.tx_freq    = Fc
rad_params.tx_gain    = 10

rad      = pyaf.radio.Radio_USRP(rad_params)
rad.n_frames = n_frames


# Code pour envoyer du texte

# source          [   "generate::U_K" ] = bb_scrambler    [   "scramble::X_N1"]
# bb_scrambler    [   "scramble::X_N2"] = bch_encoder     [     "encode::U_K" ]
# bch_encoder     [     "encode::X_N" ] = ldpc_encoder    [     "encode::U_K" ]
# ldpc_encoder    [     "encode::X_N" ] = modem           [   "modulate::X_N1"]
# framer          [   "generate::Y_N1"] = modem           [   "modulate::X_N2"]
# framer          [   "generate::Y_N2"] = pl_scrambler    [   "scramble::X_N1"]
# shp_filter      [     "filter::X_N1"] = pl_scrambler    [   "scramble::X_N2"]




# sequence = threaded_sequence(source["generate"]) # py_aff3ct.tools.sequence.Sequence
# sequence.export_dot("test.dot")
# for lt in sequence.get_tasks_per_types():
#     for t in lt:
#         t.stats = True
#         #t.debug = True
#         #t.set_debug_precision(8)
#         #t.set_debug_limit(10)


# sequence.start()
# initial_time = time.time()
# while sequence.is_alive():
#     #print(source          [   "generate::U_K" ][:])
#     print(bb_scrambler    [   "scramble::X_N1"][:])
#     pass

# sequence.show_stats()


def display_frozen_bits(frozen_bits):
    # representation
    blue  = [0, 0, 255]
    green = [0, 255, 0]

    bits = np.ndarray((len(frozen_bits),40,3))

    for i, bit in enumerate(frozen_bits):
        if bit:
            bits[i,:] = blue
        else:
            bits[i,:] = green

    plt.imshow(bits)
    plt.title("Frozen bits of the polar code")
    plt.show()


def get_good_bits(frozen_bits):
	#gives the positions of the 'good bits' according to the frozen ones
    good_bits = []
    N = len(frozen_bits)
    for i in range(N):
        if not frozen_bits[i]:
            good_bits.append(i)
    return good_bits        
    

##Parameters
K = 512
N = 1024
p = 16200

sigma_eve = 0 #vraie valeur 1e-7
sz_in  = (1,N)
sz_out = (1,p)
sigma = 1e-9 + sigma_eve


fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K, N)
noise = aff3ct.tools.noise.Sigma(sigma)
fbgen.set_noise(noise)
frozen_bits = fbgen.generate()


good_bits = get_good_bits(frozen_bits)
mux = py_MUX(good_bits[0:8], K)
mux2 = pyaf.multiplexer.Multiplexer(good_bits[0:8], K)
enc = aff3ct.module.encoder.Encoder_polar_sys(K,N,frozen_bits)
mdm = aff3ct.module.modem.Modem_BPSK_fast(p)
padder = Padder(sz_in[1], sz_out[1])
padder2 = pyaf.padder.Padder(sz_in[1], sz_out[1])
bad_bits_src = aff3ct.module.source.Source_random_fast(K)
pad_src = aff3ct.module.source.Source_random_fast(sz_out[1]-sz_in[1])

## Modules' connection
mux2["multiplexer        ::bad_bits "] = bad_bits_src["generate    ::U_K "]
mux2["multiplexer        ::good_bits "] = source["generate    ::U_K "]
#bad_bits_src["generate"] = source["generate    ::status "]
#pad_src["generate"] = source["generate    ::status "]
enc["encode        ::U_K "] = mux2["multiplexer    ::sig_mux_out "]
padder2["pad2        ::r_in "] = pad_src["generate    ::U_K "]
padder2["pad2        ::p_in "] = enc["encode     ::X_N "]
padder2["pad2        ::p_out "] = mdm["modulate:: X_N1"]
framer          [   "generate::Y_N1"] =mdm["modulate:: X_N2"]
framer          [   "generate::Y_N2"] = pl_scrambler    [   "scramble::X_N1"]
shp_filter      [     "filter::X_N1"] = pl_scrambler    [   "scramble::X_N2"]
gain["imultiply::X_N"] = shp_filter      [     "filter::Y_N2"] 
rad   [       "send::X_N1"] = gain["imultiply::Z_N"]

sequence = threaded_sequence([source["generate"],bad_bits_src["generate"],pad_src["generate"]],1) # py_aff3ct.tools.sequence.Sequence
sequence.export_dot("test.dot")
for lt in sequence.get_tasks_per_types():
    for t in lt:
        t.stats = True
        # t.debug = True
        # t.set_debug_precision(8)
        # t.set_debug_limit(10)
        
sequence.start()
initial_time = time.time()
while sequence.is_alive():
    #print(rad   [       "send::X_N1"][:])
    pass

sequence.show_stats()
