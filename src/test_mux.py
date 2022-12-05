# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 22:49:54 2022

@author: elias
"""

import numpy as np

def multiplexeur(good_bits, positions, N_code):
    sig_mux = np.random.randint(2, size=N_code)     
    for i in range(len(positions)):
        if positions[i] > N_code or positions[i] < 0:
            raise ValueError("Error: positions["+ str(i) +"] (" + str(positions[i]) + ") must be between 0 and N_code (" + str(N_code) + ")")
        if len(positions) != len(good_bits):
            raise ValueError("Error: len(positions) != len(good_bits) (" + str(len(positions)) + " != " + str(len(good_bits)) + ")")
        sig_mux[positions[i]] = good_bits[i]        
    return sig_mux

def demultiplexeur(sig_mux, positions, N_code):
    sig_demux = np.zeros(len(positions))
    for i in range(len(positions)):
        if positions[i] > N_code or positions[i] < 0:
            raise ValueError("Error: positions["+ str(i) +"] (" + str(positions[i]) + ") must be between 0 and N_code (" + str(N_code) + ")")
        sig_demux[i] = sig_mux[positions[i]]
    return sig_demux

def get_good_bits(frozen_bits):
    good_bits = []
    N = len(frozen_bits)
    for i in range(N):
        if frozen_bits[i] == 0:
            good_bits.append(i)
    return good_bits 

def test_get_good_bits():
    good_bits = [2, 3, 4, 6]
    frozen = np.array([1, 1, 0, 0, 0, 1, 0], dtype=int)
    good = get_good_bits(frozen)

    assert([good_bits[i] == good[i] for i in range(len(good))])

def test_chaine_MUX():
    N_code = 1024 #taille du code
    pos = np.array([122, 627, 4, 422, 188], dtype=int) #position des bits bons pour bob et mauvais pour eve
    good_bits = np.array([2, 5, 99, 4, 8], dtype=int) #ce qui vient de la source
    
    sig_mux = multiplexeur(good_bits, pos, N_code)
    sig_demux = demultiplexeur(sig_mux, pos, N_code)

    assert([good_bits[i] == sig_demux[i] for i in range(len(sig_demux))])

