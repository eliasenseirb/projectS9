from dotenv import load_dotenv
import sys
import os
from pad import Pad
import numpy as np

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc
from py_aff3ct.module.py_module import Py_Module

class Padder():

    def __init__(self, init_size: int, final_size: int):
        self.init_size = init_size      # size before padding
        self.final_size = final_size    # size after padding
        self.name = "padder"            # module name
        self.pad_size = self.final_size - self.init_size

    def pad(self, sig_in: np.ndarray, sig_out: np.ndarray):
        """Pad the received signal so that it has final_size components"""
        
        # return padded signal
        
        sig_out[0,:] = np.concatenate((sig_in, np.zeros((1,self.pad_size), dtype=np.int32)), axis=1, dtype=np.int32)
        
        return 0

    def unpad(self, padded_sig: np.ndarray, sig_out: np.ndarray):
        """Extract the first init_size components of sig"""

        sig_out[0,:] = padded_sig[0, 0:self.init_size]
        
        return 0
