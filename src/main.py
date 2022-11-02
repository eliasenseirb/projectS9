"""

This file is made to test things.

Before run, do:
$ export PYTHONPATH=../../Aff3ct/py_aff3ct/build/lib

"""


import numpy as np
import sys
import os
from dotenv import load_dotenv

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))


import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc

encoder_polar = af_enc.Encoder_polar(500,500,500*[False])

encoder_polar.info()