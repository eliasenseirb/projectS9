"""

This file is made to test things.

Inspiration:
    py_aff3ct/examples/full_python/bfer_polar.py

Description of the simulation:
    EbN0 = 4
    BPSK modulation
    Systematic polar encoder and decoder
    AWGN channel
"""


import numpy as np
import sys
import os
from dotenv import load_dotenv
import time
import math
import matplotlib.pyplot as plt
import cv2

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))
sys.path.append(os.getenv("PYAF_PATH"))
sys.path.append("../"+os.getenv("PYAF_PATH"))


import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc
import pyaf
from pyaf.splitter import Splitter
from pyaf.multiplexer import Multiplexer
from source_nomod import Source

# -- PARAMETRES
K = 512      # taille a l'entree de l'encodeur
sec_K = 64   # nombre de bits utiles
N = 1024     # taille a la sortie de l'encodeur
ebn0 = 60    # SNR

esn0 = ebn0 + 10*math.log10(K/N)
sigma = 1/(math.sqrt(2)*10**(esn0/20))

img =cv2.imread("img/oeil_gris.jpg")[:,:,0] # image grayscale
img_shape = img.shape

def format_img(img: list[int], img_shape: tuple[int, int]) -> np.ndarray :
    """Transforme une liste d'entiers en tableau numpy d'uint8"""
    if len(img) != 8*img_shape[0]*img_shape[1]:
        raise ValueError(f"Erreur ! La taille de la liste {len(img)} ne correspond pas au format d'image ({img_shape[0]}, {img_shape[1]})")

    img_uint8 = [np.uint8(x) for x in img]
    img_reshaped = np.reshape(img_uint8, img_shape)

    return img_reshaped

img_rx = np.ndarray(shape=img_shape, dtype=np.uint8)

# -- CHAINE DE COM

# -- -- BITS GELES
fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K,N)
noise = aff3ct.tools.noise.Sigma(sigma)
fbgen.set_noise(noise)
frozen_bits = fbgen.generate()

# -- Source
src = Source(img, K)

# -- Splitter
splt = Splitter(src.img_bin, len(src.img_bin), K)

# -- encoder
enc = aff3ct.module.encoder.Encoder_polar_sys(K, N, frozen_bits)

# -- decoder
dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(K, N, frozen_bits)

# -- modulator
mdm = aff3ct.module.modem.Modem_BPSK_fast(N)

# -- noise generator
gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST

# -- channel
chn = aff3ct.module.channel.Channel_AWGN_LLR(N, gen)

# -- monitor
mnt = aff3ct.module.monitor.Monitor_BFER_AR(K,1000,100)

# -- Sigma sockets
sigma = np.ndarray(shape = (1,1), dtype=np.float32)

enc["encode::U_K"] = splt["Split::bit_seq"]
mdm["modulate::X_N1"] = enc["encode::X_N"]
chn["add_noise::X_N"] = mdm["modulate::X_N2"]
mdm["demodulate::Y_N1"] = chn["add_noise::Y_N"]
dec["decode_siho::Y_N"] = mdm["demodulate::Y_N2"]
splt["Collect::buffer"] = dec["decode_siho::V_K"]
mnt["check_errors::U"] = splt["Split::bit_seq"]
mnt["check_errors::V"] = splt["Collect::through"]
chn["add_noise::CP"] = sigma
mdm["demodulate::CP"] = sigma

seq = aff3ct.tools.sequence.Sequence(splt["Split"], mnt["check_errors"], 1)

# plt.ion()
# seq.export_dot("Splitter_test_seq.dot")
fig = plt.figure()
fig.canvas.draw()
ax = plt.subplot(111)
im = ax.imshow(img_rx, cmap='gist_gray')


while True:
    print("Loop")
    while not seq.is_done():
        seq.exec_step()

    src.bin2img(img_rx, splt.get_rx())
    # img_uint8 = format_img(img_rx, img_shape)
    
    mnt.reset()
    im.set_data(img_rx)
    
    im.draw(fig.canvas.renderer)
    plt.pause(.5)
    time.sleep(1)