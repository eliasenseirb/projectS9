import pytest
from padder import Padder
import numpy as np


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