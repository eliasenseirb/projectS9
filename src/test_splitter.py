import numpy as np
import os, sys

from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))
sys.path.append(os.getenv("PYAF_PATH"))
sys.path.append("../"+os.getenv("PYAF_PATH"))

from pyaf.splitter import Splitter
from source_nomod import Source

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc

import pytest


def generate_splitter():
    """Genere un splitter pour les tests"""
    img = [0,1,0,1]
    img_sz = 4
    sec_sz = 1

    return Splitter(img, img_sz, sec_sz)

def init_seq():
    """Genere une sequence de test"""
    img = np.array([[1,2],[3,4]], dtype=np.int32)
    img_sz = 4 # octets
    sec_sz = 8 # bits

    src = Source(img, sec_sz)
    img_bin = src.img_bin
    garbage = np.ndarray((1,8), dtype=np.int32)

    splt = Splitter(img_bin, len(img_bin), sec_sz)
    mnt = aff3ct.module.monitor.Monitor_BFER_AR(sec_sz,1, max_n_frames=4)
    
    splt["Collect::buffer"] = splt["Split::bit_seq"]
    garbage = splt["Collect::through"]
    """mnt["check_errors::U"] = splt["Split::bit_seq"]
    mnt["check_errors::V"] = splt["Split::bit_seq"]"""
    seq = aff3ct.tools.sequence.Sequence(splt["Split"], splt["Collect"], 1)

    for lt in seq.get_tasks_per_types():
        for t in lt:
            t.debug = True
            t.set_debug_limit(10)

    return seq, splt


def test_splitter_module_generates_properly():
    splt = generate_splitter()

    assert(splt is not None)

def test_splitter_module_can_return_buffer_properly():
    splt = generate_splitter()
    
    buff = splt.get_rx()

    assert(buff is not None)

def test_splitter_send_and_receive_properly():
    (seq, splt) = init_seq()
    
    while (not seq.is_done()):
        seq.exec_step()

    buffer = splt.get_rx()

    assert(buffer is not None)
    assert(len(buffer) > 0)

    img_tx = splt.get_tx()
    img_rx = splt.get_rx()
    
    for i in range(len(img_tx)):
        assert(img_tx[i]==img_rx[i])

def test_splitter_send_and_receive_properly_wrap_work():
    (seq, splt) = init_seq()
    
    for i in range(128):
        
        seq.exec_step()

    buffer = splt.get_rx()

    assert(buffer is not None)
    assert(len(buffer) > 0)

    img_tx = splt.get_tx()
    img_rx = splt.get_rx()
    
    for i in range(len(img_tx)):
        assert(img_tx[i]==img_rx[i])


if __name__ == '__main__':
    (seq, splt) = init_seq()

    seq.exec()