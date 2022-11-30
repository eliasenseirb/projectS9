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

class Pad(aff3ct.module.Task):
    """Pad a signal from an initial size to a final size"""

    def __init__(self):
        super().__init__()



    def exec(self):
        breakpoint()
        in_sig = 0

