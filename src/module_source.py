import numpy as np
import sys
from dotenv import load_dotenv
import os

load_dotenv()
#print(f"Working in {os.getcwd()}")
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))

#print(f"Syspath: {sys.path}")

import py_aff3ct
from py_aff3ct.module.py_module import Py_Module


import cv2



# Step 1
class source(Py_Module):

    # Step 2
    def img2bin(self, img, binary_sequence):
        """
        Description : Permet convertir une image en séquence binaire

        Input   : img               =>  (numpy.ndarray) l'image que l'on souhaite transmettre (en niveau de gris d'une taille 150-150-1)
        Output  : binary_sequence   =>  (numpy.ndarray) la suite de bit correspondant à l'image a envoyer
        """
        img=img.astype(int)
        vect_img=img.reshape(-1)
        str_binary_sequence=''.join([de2bi(x)for x in vect_img])
        tab=list(str_binary_sequence)
        binary_sequence = [int(x) for x in tab]
        binary_sequence = np.array(binary_sequence)
        return 0


    def bin2img(self, img, binary_sequence):
        """
        Description : Permet convertir une séquence binaire en image

        Input   : binary_sequence   =>  (numpy.ndarray)           la suite de bit reçu correspondant à l'image envoyée
        Output  : img               =>  (numpy.ndarray)           l'image que l'on a reçu (en niveau de gris)
        """
        size=int(len(binary_sequence)/8)
        binary_sequence=binary_sequence.tolist()
        height_bits=[]
        tab_dec=[]
        for i in range (size):
            height_bits=binary_sequence[i*8:(i+1)*8]
            dec=int(''.join(str(x) for x in height_bits),2)
            tab_dec.append(dec)

        tab_dec=np.asarray(tab_dec)
        img=tab_dec.reshape([150,150])
        return 0


    def de2bi(self, num):
        """
        Description : Permet convertir un nombre décimale en binaire

        Input   : num               =>  (numpy.int64)   un entier à convertir en déquence de bit
        Output  : binary            =>  (str)           sequence de 8 bits correspondant a num
        """
        binary = bin(num).replace("0b","")
        while len(binary)<8:
            tab_bin=list(binary)
            tab_bin.insert(0,'0')
            binary= ''.join(tab_bin)
        return binary


    # Step 3
    def __init__(self, img, N):
        # __init__ (step 3.1)
        Py_Module.__init__(self) # Call the aff3ct Py_Module __init__
        self.name = "source"   # Set your module's name

        # __init__ (step 3.2)
        Tx = self.create_task("img2bin") # create a task for your module
        Rx = self.create_task("bin2img") # create a task for your module

        # __init__ (step 3.3)
        simg_Tx = self.create_socket_in (Tx, "img", N, np.int32  ) # create an input socket for the task Tx
        sbin_Tx = self.create_socket_out(Tx, "binary_sequence", N, np.int32) # create an output socket for the task Tx

        sbin_Rx = self.create_socket_in (Rx, "binary_sequence", 8*N, np.int32) # create an output socket for the task Tx
        simg_Rx = self.create_socket_out(Rx, "img", N, np.int32  ) # create an input socket for the task Tx
        # __init__ (step 3.4)

        self.create_codelet(Tx, lambda slf, lsk, fid: slf.img2bin(lsk[simg_Tx], lsk[sbin_Tx])) # create codelet
        self.create_codelet(Rx, lambda slf, lsk, fid: slf.bin2img(lsk[simg_Rx], lsk[sbin_Rx])) # create codelet