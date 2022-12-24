from dotenv import load_dotenv
import sys
import os
from Modules.pad import Pad
import numpy as np

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc
from py_aff3ct.module.py_module import Py_Module

class Padder(Py_Module):

    def __init__(self, init_size: int, final_size: int):
        Py_Module.__init__(self)        # make it a module
        self.init_size = init_size      # size before padding
        self.final_size = final_size    # size after padding
        self.name = "padder"            # module name
        self.pad_size = self.final_size - self.init_size

        self.pattern = np.array([[0,1]], dtype=np.float32)
        self.pad_sig = np.tile(self.pattern, self.pad_size//2)

        # odd case
        if self.pad_size % 2 != 0:
            self.pad_sig = np.concatenate((self.pad_sig, np.array([[0]], dtype=np.float32)), axis=1, dtype=np.float32)

        pad   = self.create_task("pad")
        unpad = self.create_task("unpad")
        unpad_test = self.create_task("unpad_test")

        s_pad_in  = self.create_socket_in(pad,   "p_in",  init_size, np.float32)
        s_pad_out = self.create_socket_out(pad, "p_out", final_size, np.float32)

        # cas reel (canal)
        s_unpad_in  = self.create_socket_in(unpad,   "u_in", final_size, np.float32)
        s_unpad_out = self.create_socket_out(unpad, "u_out",  init_size, np.float32)

        # tests (sans canal)
        s_test_unpad_in  = self.create_socket_in(unpad_test,   "u_in_t", final_size, np.float32)
        s_test_unpad_out = self.create_socket_out(unpad_test, "u_out_t",  init_size, np.float32)

        # create codelets
        self.create_codelet(pad,   lambda slf, lsk, fid: slf.pad(  lsk[s_pad_in],   lsk[s_pad_out]))
        self.create_codelet(unpad, lambda slf, lsk, fid: slf.unpad(lsk[s_unpad_in], lsk[s_unpad_out]))
        self.create_codelet(unpad_test, lambda slf, lsk, fid: slf.unpad(lsk[s_test_unpad_in], lsk[s_test_unpad_out]))

    def pad(self, sig_in: np.ndarray, sig_out: np.ndarray):
        """Pad the received signal so that it has final_size components"""
        
        # return padded signal        
        sig_out[0,:] = np.concatenate((sig_in, self.pad_sig), axis=1, dtype=np.float32)
        return 0

    def unpad(self, padded_sig: np.ndarray, sig_out: np.ndarray):
        """Extract the first init_size components of sig"""
    
        sig_out[0,:] = padded_sig[0, 0:self.init_size]

        return 0
