#!/usr/bin/env python3

import numpy as np
import sys
import os
from dotenv import load_dotenv
import time
import math
import matplotlib.pyplot as plt

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))


import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc


K = 512
N = 1024
ebn0_min = 0
ebn0_max = 4.0
ebn0_step = 0.25

ebn0 = np.arange(ebn0_min,ebn0_max,ebn0_step)
esn0 = ebn0 + 10 * math.log10(K/N)
esn02 = ebn0 - 3 + 10 * math.log10(K/N) #decalage de 3dB
sigma_vals = 1/(math.sqrt(2) * 10 ** (esn0 / 20))

sigma_vals2 = 1/(math.sqrt(2) * 10 ** (esn02 / 20)) #nv sigma

fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K, N)
noise = aff3ct.tools.noise.Sigma(sigma_vals[0])
fbgen.set_noise(noise)
frozen_bits = fbgen.generate()

#pour le 2e canal
fbgen2 = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K, N)
noise2 = aff3ct.tools.noise.Sigma(sigma_vals2[0])
fbgen2.set_noise(noise2)
frozen_bits2 = fbgen2.generate()

src = aff3ct.module.source.Source_random_fast(K, 12)
enc = aff3ct.module.encoder.Encoder_polar_sys(K,N,frozen_bits)
dec = aff3ct.module.decoder.Decoder_polar_SC_fast_sys(K,N,frozen_bits)
mdm = aff3ct.module.modem.Modem_BPSK_fast(N)
gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST
chn = aff3ct.module.channel.Channel_AWGN_LLR(N, gen)
mnt = aff3ct.module.monitor.Monitor_BFER_AR(K, 1000)

#Pour le 2e canal
chn2 = aff3ct.module.channel.Channel_AWGN_LLR(N, gen)
mdm2 = aff3ct.module.modem.Modem_BPSK_fast(N)
dec2 = aff3ct.module.decoder.Decoder_polar_SC_fast_sys(K,N,frozen_bits2)
mnt2 = aff3ct.module.monitor.Monitor_BFER_AR(K, 1000)


sigma = np.ndarray(shape = (1,1),  dtype = np.float32)
sigma2 = np.ndarray(shape = (1,1),  dtype = np.float32) #pour le 2e canal


enc["encode       ::U_K "].bind(src["generate   ::U_K "])
mdm["modulate     ::X_N1"].bind(enc["encode     ::X_N "])
chn["add_noise    ::X_N "].bind(mdm["modulate   ::X_N2"])
mdm["demodulate   ::Y_N1"].bind(chn["add_noise  ::Y_N "])
dec["decode_siho  ::Y_N "].bind(mdm["demodulate ::Y_N2"])
mnt["check_errors ::U   "].bind(src["generate   ::U_K "])
mnt["check_errors ::V   "].bind(dec["decode_siho::V_K "])
chn["add_noise    ::CP  "].bind(                 sigma  )
mdm["demodulate   ::CP  "].bind(                 sigma  )

chn2["add_noise    ::X_N "].bind(mdm["modulate   ::X_N2"]) #data du modulateur
mdm2["demodulate   ::Y_N1"].bind(chn2["add_noise  ::Y_N "]) #on renvoie vers un nv demod
dec2["decode_siho  ::Y_N "].bind(mdm2["demodulate ::Y_N2"]) #suite
mnt2["check_errors ::U   "].bind(src["generate   ::U_K "]) #venant de la source sur le nv moniteur
mnt2["check_errors ::V   "].bind(dec2["decode_siho::V_K "]) #venant du nv decodeur sur nv moniteur
chn2["add_noise    ::CP  "].bind(                 sigma2  ) #nv valeur de sigma sur le bloc
mdm2["demodulate   ::CP  "].bind(                 sigma2  ) #nv valeur de sigma sur le bloc


#src("generate"    ).stats = True
#enc("encode"      ).stats = True
#mdm("modulate"    ).stats = True
#chn("add_noise"   ).stats = True
#mdm("demodulate"  ).stats = True
#dec("decode_siho" ).stats = True
#mnt("check_errors").stats = True

seq  = aff3ct.tools.sequence.Sequence(src("generate"), mnt("check_errors"), 4)
seq2  = aff3ct.tools.sequence.Sequence(src("generate"), mnt2("check_errors"), 4)

fer = np.zeros(len(ebn0))
ber = np.zeros(len(ebn0))

#pour le 2e canal
fer2 = np.zeros(len(ebn0))
ber2 = np.zeros(len(ebn0))

fig = plt.figure()
ax = fig.add_subplot(111)
line1,line2,line3,line4 = ax.semilogy(ebn0, fer, 'r-', ebn0, ber, 'b--', ebn0, fer2, 'g-', ebn0, ber2, 'm--') # Returns a tuple of line objects, thus the comma
plt.ylim((1e-6, 1))

print("Eb/NO | FRA | BER | FER | Tpt ")
for i in range(len(sigma_vals)):
	sigma[:] = sigma_vals[i]
	noise = aff3ct.tools.noise.Sigma(sigma_vals[i])
	fbgen.set_noise(noise)
	frozen_bits = fbgen.generate()
	enc.set_frozen_bits(frozen_bits)
	dec.set_frozen_bits(frozen_bits)

    #partie pour le 2e canal
	sigma2[:] = sigma_vals2[i]
	noise2 = aff3ct.tools.noise.Sigma(sigma_vals2[i])
	fbgen2.set_noise(noise2)
	frozen_bits2 = fbgen2.generate()
	dec2.set_frozen_bits(frozen_bits2)

	t = time.time()
	seq.exec()
	seq2.exec()
	elapsed = time.time() - t
	total_fra = mnt.get_n_analyzed_fra()

	ber[i] = mnt.get_ber()
	fer[i] = mnt.get_fer()
    
    #2e canal
	ber2[i] = mnt2.get_ber()
	fer2[i] = mnt2.get_fer()


	tpt = total_fra * K * 1e-6/elapsed
	print( ebn0[i] , "|",  total_fra, "|", ber[i] ,"|", fer[i] , "|", tpt)

	mnt.reset()

	line1.set_ydata(fer)
	line2.set_ydata(ber)
	line3.set_ydata(fer2)
	line4.set_ydata(ber2)
	fig.canvas.draw()
	fig.canvas.flush_events()
	plt.pause(1e-6)

seq.show_stats()
plt.show()