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
from pyaf.padder import Padder

from source_nomod import Source
from params import Bob, Eve

BOB = 0
EVE = 1

Simulation_type = EVE

# -- PARAMETRES
ebn0 = 12
params_bob = Bob(ebn0)
params_eve = Eve(ebn0)

if (Simulation_type == BOB):
    params = params_bob
else:
    params = params_eve


img =cv2.imread("img/oeil_gris.jpg")[:,:,0] # image grayscale
img_shape = img.shape


def convert_frozen_bits(frozen_bits):
    # representation
    blue  = [0, 0.44, 0.74]
    green = [1, 1, 0.13]

    bits = np.ndarray((len(frozen_bits),40,3))
    for i, bit in enumerate(frozen_bits):
        if bit:
            bits[i,:] = blue
        else:
            bits[i,:] = green

    return bits

def display_frozen_bits(frozen_bits):
    
    bits = convert_frozen_bits(frozen_bits)

    plt.figure()
    
    plt.imshow(bits)
    plt.title("Frozen bits of the polar code")
    return bits

def display_common_frozen_bits(bob_frozen_bits, eve_frozen_bits):
    blue  = [0, 0.44, 0.74]  # frozen bits
    green = [1, 1, 0.13] # bob information bits
    red   = [0.85, 0.33, 0.1]  # common bits (random)

    joint_bits = np.ndarray((len(bob_frozen_bits), 40, 3))

    bob_bits = convert_frozen_bits(bob_frozen_bits)
    eve_bits = convert_frozen_bits(eve_frozen_bits)

    for i, bit in enumerate(bob_frozen_bits):
        if bit: # frozen bit anyway
            joint_bits[i,:] = blue
        else:
            if eve_frozen_bits[i]: # information bit
                joint_bits[i,:] = green
            else:
                joint_bits[i,:] = red

    plt.figure()
    
    
    plt.subplot(131)
    
    plt.imshow(bob_bits)
    plt.axis('off') 

    plt.subplot(132)
    plt.imshow(eve_bits)
    plt.axis('off')

    plt.subplot(133)
    plt.imshow(joint_bits)
    plt.axis('off')

    plt.figure()
    plt.imshow(bob_bits)
    plt.axis('off')
    plt.savefig('bob.png', format='png', bbox_inches='tight')
    plt.close()

    plt.figure()
    plt.imshow(eve_bits)
    plt.axis('off')
    plt.savefig('eve.png', format='png', bbox_inches='tight')
    plt.close()

    plt.figure()
    plt.imshow(joint_bits)
    plt.axis('off')
    plt.savefig('joint.png', format='png', bbox_inches='tight')
    plt.close()




def format_img(img: list[int], img_shape: tuple[int, int]) -> np.ndarray :
    """Transforme une liste d'entiers en tableau numpy d'uint8"""
    if len(img) != 8*img_shape[0]*img_shape[1]:
        raise ValueError(f"Erreur ! La taille de la liste {len(img)} ne correspond pas au format d'image ({img_shape[0]}, {img_shape[1]})")

    img_uint8 = [np.uint8(x) for x in img]
    img_reshaped = np.reshape(img_uint8, img_shape)

    return img_reshaped

def all_no(bits_Bob: list[bool], bits_Eve: list[bool]):
	"""Fait une liste complete des bits sur lesquels ne pas envoyer"""
	out = [False for i in range(len(bits_Bob))]
	pos = []
	for i in range(len(bits_Bob)):
		out[i] = no(bits_Bob[i], bits_Eve[i])
		if out[i]:
			pos.append(i)
	return out, pos

def no(b1: bool, b2: bool):
	"""Trie les bits sur lesquels il ne faut pas envoyer"""
	return (not b1) and b2

def count(b: list[bool]):
	"""Compte les True dans une liste"""
	cnt = 0
	for bol in b:
		if bol:
			cnt+=1
	return cnt

def get_secrecy_position(frozen_bits, information_bits):
    """Trouve les positions dans la suite de K bits des
    bits de confidentialite.

    frozen_bits : list[bool] --> True si le bit est gele, False sinon
    information_bits: list[bool] --> Position des bits de confidentialite dans la liste de N bits
    """
    if information_bits == []:
        raise ValueError("No bits available for secrecy with this combination of EbN0 and penalty for Eve.")
    seq_ptr = 0
    info_idx = 0
    positions = []
    for i in range(len(frozen_bits)):
        if not frozen_bits[i]:
            # A chaque fois qu'on trouve un bit d'information
            # on avance dans la suite de K bits

            # Si cette position se trouve dans le tableau de bits
            # d'information, on la stocke
            # /!\ On travaille sous l'hypothese que les deux tableaux
            # sont tries
            
            print(f"{information_bits[info_idx]} vs {i}")
            if information_bits[info_idx] == i:
                positions.append(seq_ptr)
                info_idx += 1
            if info_idx == len(information_bits):
                return positions
            seq_ptr += 1

    return positions


img_rx = np.ndarray(shape=img_shape, dtype=np.uint8)

# -- CHAINE DE COM

# -- -- BITS GELES
fbgen_b = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(params_bob.K,params.N)
params_bob.noise = aff3ct.tools.noise.Sigma(params_bob.sigma)
fbgen_b.set_noise(params_bob.noise)
params_bob.frozen_bits = fbgen_b.generate()

fbgen_e = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(params_eve.K,params.N)
params_eve.noise = aff3ct.tools.noise.Sigma(params_eve.sigma)
fbgen_e.set_noise(params_eve.noise)
params_eve.frozen_bits = fbgen_e.generate()

mux_bits, pos_mux_bits = all_no(params_bob.frozen_bits, params_eve.frozen_bits)
params.sec_sz = count(mux_bits)

display_common_frozen_bits(params_bob.frozen_bits, params_eve.frozen_bits)

breakpoint()
"""to_remove = []
for pos in pos_mux_bits:
    if pos > params.K:
        print(f"Position invalide {pos}!!!")
        to_remove.append(pos)

for r in to_remove:
    pos_mux_bits.remove(r)
cnt=  0
"""

seq_pos = get_secrecy_position(params_bob.frozen_bits, pos_mux_bits)

for b in seq_pos:
    print(b)



"""
for i in range(params.N):
    if not mux_bits[i]:
        print(f"{i}")
        cnt+=1
print(cnt)
"""
#breakpoint()
# -- Source
src_im = Source(img, params.sec_sz)
src_rand = aff3ct.module.source.Source_random_fast(params.N, 12)
src_rand2 = aff3ct.module.source.Source_random_fast(params.K, 24)

# -- Splitter
splt = Splitter(src_im.img_bin, len(src_im.img_bin), params.sec_sz)

# -- padder
pad = Padder(params.sec_sz, params.K)

# -- encoder
enc = aff3ct.module.encoder.Encoder_polar_sys(params.K, params.N, params_bob.frozen_bits)

# -- multiplexer
mux = Multiplexer(seq_pos, count(mux_bits), params.K)

# -- decoder
dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(params.K, params.N, params_bob.frozen_bits)

# -- modulator
mdm = aff3ct.module.modem.Modem_BPSK_fast(params.N)

# -- noise generator
gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST

# -- channel
chn = aff3ct.module.channel.Channel_AWGN_LLR(params.N, gen)

# -- monitor
mnt = aff3ct.module.monitor.Monitor_BFER_AR(params.sec_sz,1000,100)

# -- Sigma sockets
sigma = np.ndarray(shape = (1,1), dtype=np.float32)
sigma[0,0] = params.sigma


mux["multiplexer::good_bits"] = splt["Split::bit_seq"]
mux["multiplexer::bad_bits"] = src_rand2["generate::U_K"]
enc["encode::U_K"] = mux["multiplexer::sig_mux_out"]
mdm["modulate::X_N1"] = enc["encode::X_N"]
chn["add_noise::X_N"] = mdm["modulate::X_N2"]
mdm["demodulate::Y_N1"] = chn["add_noise::Y_N"]
dec["decode_siho::Y_N"]  = mdm["demodulate::Y_N2"]
mux["demultiplexer::mux_sequence"] = dec["decode_siho::V_K"] 
splt["Collect::buffer"] = mux["demultiplexer::good_bits"]
mnt["check_errors::U"] = splt["Split::bit_seq"]
mnt["check_errors::V"] = splt["Collect::through"]
chn["add_noise::CP"] = sigma
mdm["demodulate::CP"] = sigma

seq = aff3ct.tools.sequence.Sequence(splt["Split"] , mnt["check_errors"], 1)

seq.export_dot("demonstrateur.dot")

"""
for lt in seq.get_tasks_per_types():
    for t in lt:
        t.debug = True
        t.set_debug_limit(10)
"""
# plt.ion()
# seq.export_dot("Splitter_test_seq.dot")
fig = plt.figure()
fig.canvas.draw()
ax = plt.subplot(111)
im = ax.imshow(img_rx, cmap='gist_gray')

cnt = 0
while True:
    #print("Loop")
    while not seq.is_done():
        seq.exec_step()
    
    
    src_im.bin2img(img_rx, splt.get_rx())
    # img_uint8 = format_img(img_rx, img_shape)
    mnt.reset()
    im.set_data(img_rx)
    #print(np.squeeze(mutinf))
        
    im.draw(fig.canvas.renderer)
    
    fig.canvas.flush_events()
    
    plt.pause(.01)
    #time.sleep(1)
    if cnt == 0:
        breakpoint()
        cnt = 1
    #breakpoint()

"""
def update_plot(img, imh=imh, renderer=renderer):
    imh.set_data(img)
    imh.draw(renderer)
    plt.pause(.5)

while:

    update_plot(img)"""