#!/usr/bin/env python3


import numpy as np
import sys
import os
from dotenv import load_dotenv
import time
import math
import matplotlib.pyplot as plt
from Mod_MUX import py_MUX 



load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))


import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc

def display_frozen_bits(frozen_bits):
    # representation
    blue  = [0, 0, 255]
    green = [0, 255, 0]

    bits = np.ndarray((len(frozen_bits),40,3))

    for i, bit in enumerate(frozen_bits):
        if bit:
            bits[i,:] = blue
        else:
            bits[i,:] = green


    plt.imshow(bits)
    plt.title("Frozen bits of the polar code")
    plt.show()

def get_good_bits(frozen_bits):
    good_bits = []
    N = len(frozen_bits)
    for i in range(N):
        if not frozen_bits[i]:
            good_bits.append(i)
    return good_bits        
    


K = 512
N = 1024
ebn0_min = 0
ebn0_max = 2.5
ebn0_step = 0.25

ebn0 = np.arange(ebn0_min,ebn0_max,ebn0_step)
esn0 = ebn0 + 10 * math.log10(K/N)
sigma_vals = 1/(math.sqrt(2) * 10 ** (esn0 / 20))


fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K, N)
noise = aff3ct.tools.noise.Sigma(sigma_vals[0])
fbgen.set_noise(noise)
frozen_bits = fbgen.generate()

src = aff3ct.module.source.Source_random_fast(8, 12)

# MUX
good_bits = get_good_bits(frozen_bits)
print('GOOD_BITS = ', good_bits[0:8])
mux = py_MUX(good_bits[0:8], K)
mux2 = py_MUX(good_bits[0:8], K)



#Bob
enc = aff3ct.module.encoder.Encoder_polar_sys(K,N,frozen_bits)
dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(K,N,frozen_bits)
mdm = aff3ct.module.modem.Modem_BPSK_fast(N)
gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST
chn = aff3ct.module.channel.Channel_AWGN_LLR(N, gen)
mnt = aff3ct.module.monitor.Monitor_BFER_AR(8, 1000)
mnt_ex = aff3ct.module.monitor.Monitor_BFER_AR(K, 0)

#Eve
dec2 = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(K,N,frozen_bits)
mdm2 = aff3ct.module.modem.Modem_BPSK_fast(N)
chn2 = aff3ct.module.channel.Channel_AWGN_LLR(N,gen)
mnt2 = aff3ct.module.monitor.Monitor_BFER_AR(8,0)


sigma = np.ndarray(shape = (1,1),  dtype = np.float32)
sigma_wiretap = np.ndarray(shape = (1,1),  dtype = np.float32)


mux["multiplexer        ::good_bits "] = src["generate    ::U_K "]
enc["encode        ::U_K "] = (mux["multiplexer    ::sig_mux_out "])
mdm["modulate     ::X_N1"] = (enc["encode     ::X_N "])
chn["add_noise    ::X_N "].bind(mdm["modulate   ::X_N2"])
mdm["demodulate   ::Y_N1"].bind(chn["add_noise  ::Y_N "])
dec["decode_siho  ::Y_N "].bind(mdm["demodulate ::Y_N2"])

mnt["check_errors ::U   "].bind(src["generate   ::U_K "])
mux["demultiplexer  ::sig_mux_in   "].bind(dec["decode_siho ::V_K "])
mnt["check_errors  ::V  "].bind(mux["demultiplexer  ::sig_demux"])

chn["add_noise    ::CP  "].bind(                 sigma  )
mdm["demodulate   ::CP  "].bind(                 sigma  )


chn2["add_noise    ::X_N "].bind(mdm["modulate    ::X_N2"])
mdm2["demodulate   ::Y_N1"].bind(chn2["add_noise  ::Y_N "])
dec2["decode_siho  ::Y_N "].bind(mdm2["demodulate ::Y_N2"])
mnt2["check_errors  ::U  "].bind(src["generate    ::U_K "])

mux2["demultiplexer  ::sig_mux_in   "].bind(dec2["decode_siho ::V_K "])
mnt2["check_errors  ::V  "].bind(mux2["demultiplexer  ::sig_demux"])

#mnt2["check_errors  ::V  "].bind(dec2["decode_siho ::V_K "])
chn2["add_noise    ::CP  "].bind(          sigma_wiretap  )
mdm2["demodulate   ::CP  "].bind(          sigma_wiretap  )

#renvoie le PER pour la courbe d'exemple
mnt_ex["check_errors ::U   "].bind(mux["multiplexer    ::sig_mux_out "])
mnt_ex["check_errors ::V   "].bind(dec["decode_siho::V_K "])

#src("generate"    ).stats = True
#enc("encode"      ).stats = True
#mdm("modulate"    ).stats = True
#chn("add_noise"   ).stats = True
#mdm("demodulate"  ).stats = True
#dec("decode_siho" ).stats = True
#mnt("check_errors").stats = True

seq  = aff3ct.tools.sequence.Sequence(src["generate"], 1)

"""for lt in seq.get_tasks_per_types():
	for t in lt:
		t.debug = True
		t.set_debug_limit(10)
	"""
fer = np.zeros(len(ebn0))
ber = np.zeros(len(ebn0))

fer_w = np.zeros(len(ebn0))
ber_w = np.zeros(len(ebn0))

fig = plt.figure()
ax = fig.add_subplot(111)
line1,line2,line3,line4, = ax.semilogy(ebn0, fer, 'r-', ebn0, ber, 'b--', ebn0, fer_w, 'g-', ebn0, ber_w, 'm--') # Returns a tuple of line objects, thus the comma

ax.set_title("Test wiretap")
line1.set_label("fer")
line2.set_label("ber")
line3.set_label("fer wiretap")
line4.set_label("ber wiretap")
ax.legend()
ax.set_xlabel("SNR (dB)")
ax.set_ylabel("Pe")
plt.ylim((1e-6, 1))



print("Eb/NO | FRA | BER | FER | FER2 | Tpt ")
for i in range(len(sigma_vals)):
	sigma[:] = sigma_vals[i]
	noise = aff3ct.tools.noise.Sigma(sigma_vals[i])
	fbgen.set_noise(noise)
	frozen_bits = fbgen.generate()
	enc.set_frozen_bits(frozen_bits)
	dec.set_frozen_bits(frozen_bits)

	t = time.time()
	seq.exec()
	elapsed = time.time() - t
	total_fra = mnt.get_n_analyzed_fra()

	ber[i] = mnt.get_ber()
	fer[i] = mnt.get_fer()
	ber_w[i] = mnt2.get_ber()
	fer_w[i] = mnt2.get_fer()
	
	fer_ex = mnt_ex.get_fer()

	tpt = total_fra * K * 1e-6/elapsed
	print( ebn0[i] , "|",  total_fra, "|", ber[i] ,"|", fer[i], "|", fer_ex , "|", tpt)

	mnt.reset()
	mnt2.reset()
	mnt_ex.reset()

	line1.set_ydata(fer)
	line2.set_ydata(ber)
	line3.set_ydata(fer_w)
	line4.set_ydata(ber_w)
	fig.canvas.draw()
	fig.canvas.flush_events()
	plt.pause(1e-6)

seq.show_stats()
plt.show()

