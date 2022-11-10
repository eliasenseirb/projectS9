from dotenv import load_dotenv
import sys
import os

import numpy as np

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc

class Padder:

    def __init__(self, init_size: int, final_size: int):
        self.init_size = init_size
        self.final_size = final_size

    def pad(self, sig: np.ndarray):
        """Pad the received signal so that it has final_size components"""
        S = sig.shape

        # get highest dimension
        if len(S)>1:
            raise ValueError("2D-signals are not handled yet.")
        
        # get dimension and axis of padding
        sig_size = S
        axis = 0

        # compute padding size
        pad_size = self.final_size - sig_size[0]

        # return padded signal
        return np.concatenate((sig, np.zeros((pad_size,))), axis=axis)

    def unpad(self, padded_sig: np.ndarray):
        """Extract the first init_size components of sig"""
        #breakpoint()
        test = padded_sig[0:self.init_size]
        return test