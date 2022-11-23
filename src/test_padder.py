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


def test_padder_as_module_pads():
    K = 1024
    N = 16384
    sz_in  = (1,K)
    sz_out = (1,N)
    mnt     = aff3ct.module.monitor.Monitor_BFER_AR(K,1000,1000)
    sig_in  = np.random.randint(0,1,sz_in, dtype=np.int32)
    sig_out = np.ndarray(sz_out, dtype=np.int32)

    src  = aff3ct.module.source.Source_random_fast(K,11)
    padder = Padder(sz_in[1], sz_out[1])


    padder["pad ::p_in"]   = src["generate::U_K"]
    padder["pad::p_out"]   = padder["unpad::u_in"]
    padder["unpad::u_out"] = mnt["check_errors::V"]
    mnt["check_errors::U"] = src["generate::U_K"]

    seq = aff3ct.tools.sequence.Sequence(src["generate"], mnt["check_errors"],1)
    
    seq.exec()

    ber = mnt.get_ber()

    assert(ber == 0)
