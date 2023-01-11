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
        """
        Description:
            Returns a random signal but with the good bits located at specific positions

        Inputs: 
            - good_bits: data to intertwine
            - positions: positions of the good channels according to weak secrecy
            - N_code: size of the code    

        Output:
            - sig_mux: a random signal with data bits at specific positions
        """
        length = len(positions)

        sig_mux[:,:] = np.random.randint(2, size=(1,N_code))

        for i in range(length):
            if positions[i] > N_code or positions[i] < 0:
                raise ValueError(f"Error: positions[{i}] ({positions[i]}) must be between 0 and N_code ({N_code})")
            if length != len(good_bits[0]):
                raise ValueError(f"Error: len(positions) != len(good_bits) ({length} != {len(good_bits[0])})")
            sig_mux[0,positions[i]] = good_bits[0,i]     
        return 0

    def demultiplexeur(self, sig_demux, sig_mux, positions, N_code):
        """
        Description:
            Returns the good bits from the intertwined signal

        Inputs: 
            - sig_mux: the intertwined signal with data bits at specific positions
            - positions: positions of the good channels according to weak secrecy
            - N_code: size of the code    

        Output:
            - sig_demux: the good bits of data
        """
        length = len(positions)
        
        sig_demux[0,:] = np.zeros(length)
        for i in range(length):
            if positions[i] > N_code or positions[i] < 0:
                raise ValueError(f"Error: positions[{i}] ({positions[i]}) must be between 0 and N_code ({N_code})")
            sig_demux[0,i] = sig_mux[0,positions[i]]      
        return 0
    

    # Step 3
    def __init__(self, positions, N_code):

        Py_Module.__init__(self) # Call the aff3ct Py_Module __init__
        self.name = "py_multiplexer"   # Set the module's name

        #MULTIPLEXER        
        t_mux = self.create_task("multiplexer") # create a task for the module
        
        good_b = self.create_socket_in (t_mux, "good_bits", 8, np.int32) # create an input socket for the task t_mux
        sig_m = self.create_socket_out(t_mux, "sig_mux_out", N_code, np.int32) # create an output socket for the task t_mux
    
        self.create_codelet(t_mux, lambda slf, lsk, fid: slf.multiplexeur(lsk[sig_m], lsk[good_b], positions, N_code)) # create codelet


        #DEMULTIPLEXER
        t_demux = self.create_task("demultiplexer") # create a task for the module
         
        sig_mux = self.create_socket_in (t_demux, "sig_mux_in", N_code, np.int32) # create an input socket for the task t_demux
        sig_dem = self.create_socket_out(t_demux, "sig_demux", 8, np.int32) # create an output socket for the task t_demux
        
        self.create_codelet(t_demux, lambda slf, lsk, fid: slf.demultiplexeur(lsk[sig_dem], lsk[sig_mux], positions, N_code)) # create codelet
        
