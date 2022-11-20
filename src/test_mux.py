# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 22:49:54 2022

@author: elias
"""

import numpy as np

def multiplexeur(bits_bons, positions, N_code):
    sig_mux = np.random.randint(2, size=N_code)     
    for i in range(len(positions)):
        assert positions[i] <= N_code and len(positions) == len(bits_bons),\
               "Error: index > len(sig_mux) or len(positions) != len(bits_bons)"
        sig_mux[positions[i]] = bits_bons[i]        
    return sig_mux

def demultiplexeur(sig_mux, positions, N_code):
    sig_demux = np.zeros(len(positions))
    for i in range(len(positions)):
        assert positions[i] <= N_code and len(positions) == len(bits_bons),\
               "Error: index > len(sig_mux) or len(positions) != len(bits_bons)"
        sig_demux[i] = sig_mux[positions[i]]
    return sig_demux


N_code = 1024 #taille du code
pos = np.array([1, 67, 422, 988], dtype=int) #position des bits bons pour bob et mauvais pour eve
bits_bons = np.array([2, 4, 6, 8], dtype=int) #ce qui vient de la source

sig_mux = multiplexeur(bits_bons, pos, N_code)
print('SIG mux : ', sig_mux)

sig_demux = demultiplexeur(sig_mux, pos, N_code)
print('SIG demux : ', sig_demux)
