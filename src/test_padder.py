import pytest
import os, sys
from padder import Padder
import numpy as np
from dotenv import load_dotenv

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))

import py_aff3ct as aff3ct

"""
def test_pad_signal_1_64_returns_signal_1_128():
    padder = Padder(64,128)
    sig = np.zeros((64,))
    padded_sig = padder.pad(sig)

    assert(padded_sig.shape == (128,))

def test_unpad_signal_1_128_returns_signal_1_64():
    padder = Padder(64,128)
    padded_sig = np.zeros((128,))
    sig_shape = (64,)

    unpadded = padder.unpad(padded_sig)

    assert(unpadded.shape == sig_shape)
"""

def test_padder_no_module_pads():
    K=1024
    N=16384
    sz_in = (1,K)
    sz_out = (1,N)
    sig_in  = np.random.randint(0,1,sz_in, dtype=np.int32)
    sig_padded = np.ndarray(sz_out, dtype=np.int32)
    sig_out = np.ndarray(sz_in, dtype=np.int32)

    padder = Padder(K,N)

    padder.pad(sig_in, sig_padded)
    padder.unpad(sig_padded, sig_out)
    
    assert(np.sum(sig_in - sig_out) == 0)




def test_padder_with_canal_no_error():
    # -- parameters
    K = 1024
    N = 16384
    sz_in  = (1,N)
    sz_out = (1,N)
    sigma = np.array([[0.001]], dtype=np.float32)
    
    # source
    src  = aff3ct.module.source.Source_random_fast(K,11)

    # mod/demod
    mdm = aff3ct.module.modem.Modem_BPSK_fast(N)
    
    # encode/decode
    fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K,N)
    noise = aff3ct.tools.noise.Sigma(sigma)
    fbgen.set_noise(noise)
    frozen_bits = fbgen.generate()
    enc  = aff3ct.module.encoder.Encoder_polar_sys(K,N,frozen_bits)
    dec  = aff3ct.module.decoder.Decoder_polar_SC_fast_sys(K,N,frozen_bits)
    
    # pad/unpad
    padder = Padder(sz_in[1], sz_out[1])
    
    # canal
    gen  = aff3ct.tools.Gaussian_noise_generator_implem.FAST
    chn = aff3ct.module.channel.Channel_AWGN_LLR(N,gen)

    # monitor
    mnt = aff3ct.module.monitor.Monitor_BFER_AR(K,1000,1)


    enc["encode         ::U_K "] = src["generate    :: U_K "]
    mdm["modulate      ::X_N1 "] = enc["encode::X_N"]
    padder["pad        ::p_in "] = mdm["modulate:: X_N2"]
    chn   ["add_noise  :: X_N "] = padder["pad         ::p_out"]
    padder["unpad      ::u_in "] = chn   ["add_noise   :: Y_N "]
    mdm["demodulate     ::Y_N1"] = padder["unpad      ::u_out"]
    dec["decode_siho     ::Y_N"] = mdm["demodulate :: Y_N2"]
    mnt   ["check_errors::  V "] = dec["decode_siho::V_K"]
    mnt["check_errors  ::   U "] = src   ["generate    :: U_K "]
    chn   ["add_noise  ::  CP "] = sigma
    mdm["demodulate       ::CP"] = sigma

    seq = aff3ct.tools.sequence.Sequence(src["generate"], mnt["check_errors"],1)
    
    seq.exec()