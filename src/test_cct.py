# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 10:45:22 2022

@author: elias
"""
import numpy as np

def concatener(sig_in, sig_cct, borne_inf, borne_sup, size_radio):
    if(borne_inf >= 0 and borne_sup >= 0 and borne_sup <= size_radio):
        sig_cct[borne_inf:borne_sup] = sig_in
    else:
        print('error: borne incorrecte')
    return sig_cct


def deconcatener(sig_dcct, sig_cct, borne_inf, borne_sup, size_radio):
	if(borne_inf >= 0 and borne_sup >= 0 and borne_sup <= size_radio):
		sig_dcct = sig_cct[borne_inf:borne_sup]
	else:
		print('error: borne incorrecte')
	return sig_dcct


N_code = 1024 #taille des mots de codes
N_radio = 16384 #taille des messages radio (16 384 normalement)
NbIter = 16 #Nombre de message à concaténer
sig_cct = np.zeros(N_radio, dtype=int) #deja le padding si besoin

for i in range(NbIter):
#encodeur pour obtenir sig_in  
    sig_in = np.random.rand(N_code)>0.5
    for j in range(N_code):
        if sig_in[j] == True:
            sig_in[j] = 1
        else:
            sig_in[j] = 0
    sig_cct = concatener(sig_in, sig_cct, i*N_code, (i+1)*N_code, N_radio)
# signal concaténé à la sortie 


sig_dcct = np.zeros((NbIter,N_code), dtype=int)
for i in range(NbIter):
#décodeur pour obtenir sig_in
    sig_dcct[i,:] = deconcatener(sig_dcct[i,:], sig_cct, i*N_code, (i+1)*N_code, N_radio)
#tableau de signaux
    
