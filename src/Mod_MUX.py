# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 16:14:55 2022

@author: elias
"""

import numpy as np
import sys
from dotenv import load_dotenv
import os

load_dotenv()

sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))

import py_aff3ct
from py_aff3ct.module.py_module import Py_Module

# Step 1
class py_MUX(Py_Module):
    def multiplexeur(self, sig_mux, good_bits, positions, N_code):
        good_bits_sz = good_bits.shape[1]
        
        print(f"sig_mux: ({sig_mux.shape}, {id(sig_mux)}), N_code: {N_code}")
        sig_mux[:,:] = np.random.randint(2, size=(1,N_code))     
        for i in range(8):
            if positions[i] > N_code or positions[i] < 0:
                raise ValueError("Error: positions["+ str(i) +"] (" + str(positions[i]) + ") must be between 0 and N_code (" + str(N_code) + ")")
            if 8 != good_bits_sz:
                raise ValueError("Error: 8 != len(good_bits) (" + str(8) + " != " + str(len(good_bits)) + ")")
            
            sig_mux[0,positions[i]] = good_bits[0,i]        
        return 0

    def demultiplexeur(self, sig_demux, sig_mux, positions, N_code):
        
        sig_demux[0,:] = np.zeros(8)
        for i in range(8):
            if positions[i] > N_code or positions[i] < 0:
                raise ValueError("Error: positions["+ str(i) +"] (" + str(positions[i]) + ") must be between 0 and N_code (" + str(N_code) + ")")
            sig_demux[0,i] = sig_mux[0,positions[i]]
        print('SIG_DEMUX = ', sig_demux)
        return 0
    

    # Step 3
    def __init__(self, positions, N_code):
        # __init__ (step 3.1)
        Py_Module.__init__(self) # Call the aff3ct Py_Module __init__
        self.name = "py_multiplexer"   # Set your module's name

        #MULTIPLEXER        
        # __init__ (step 3.2)
        t_mux = self.create_task("multiplexer") # create a task for your module
        
        # __init__ (step 3.3)
        good_b = self.create_socket_in (t_mux, "good_bits", 8, np.int32) # create an input socket for the task t_mod
        sig_m = self.create_socket_out(t_mux, "sig_mux_out", N_code, np.int32) # create an output socket for the task t_mod
    
        # __init__ (step 3.4)
        self.create_codelet(t_mux, lambda slf, lsk, fid: slf.multiplexeur(lsk[sig_m], lsk[good_b], positions, N_code)) # create codelet


        #DEMULTIPLEXER
        # __init__ (step 3.2)
        t_demux = self.create_task("demultiplexer") # create a task for your module
         
        # __init__ (step 3.3)
        sig_mux = self.create_socket_in (t_demux, "sig_mux_in", N_code, np.int32) # create an input socket for the task t_mod
        sig_dem = self.create_socket_out(t_demux, "sig_demux", 8, np.int32) # create an output socket for the task t_mod
        
        # __init__ (step 3.4)
        self.create_codelet(t_demux, lambda slf, lsk, fid: slf.demultiplexeur(lsk[sig_dem], lsk[sig_mux], positions, N_code)) # create codelet
        
