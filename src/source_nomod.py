import numpy as np
import sys
from dotenv import load_dotenv
import os
import cv2



# Step 1
class Source:

    # Step 2
    def img2bin(self):
        """
        Description : Permet convertir une image en séquence binaire

        Input   : img               =>  (numpy.ndarray) l'image que l'on souhaite transmettre (en niveau de gris d'une taille 150-150-1)
        Output  : binary_sequence   =>  (numpy.ndarray) la suite de bit correspondant à l'image a envoyer
        """
        print("[      ] Conversion en binaire.", end='')
        sys.stdout.flush() # affiche le message

        # conversion en int
        img=self.img.astype(int)

        # extraction des bits d'interet
        vect_img=img.reshape(-1)
        
        # conversion en sequence binaire
        str_binary_sequence=''.join([self.de2bi(x)for x in vect_img])
        tab=list(str_binary_sequence)
        tab = [int(x) for x in tab]

        print("\r[  OK  ] Conversion en binaire", end='\n')
        return tab

    def readimg(self, binary_sequence):
        binary_sequence[0,self.ptr_tx:self.ptr_tx+self.sec_sz] = [int(x) for x in self.img_bin[self.ptr_tx:self.ptr_tx+self.sec_sz]]
        binary_sequence[0,:] = np.array(binary_sequence)
        self.ptr_tx += self.sec_sz

    def bin2img(self, img, binary_sequence):
        """
        Description : Permet convertir une séquence binaire en image

        Input   : binary_sequence   =>  (numpy.ndarray)           la suite de bit reçu correspondant à l'image envoyée
        Output  : img               =>  (numpy.ndarray)           l'image que l'on a reçu (en niveau de gris)
        """
        size=int(len(binary_sequence)/8)
        #binary_sequence=binary_sequence.tolist()
        height_bits=[]
        tab_dec=[]
        for i in range (size):
            height_bits=binary_sequence[i*8:(i+1)*8]
            try:
                dec=int(''.join(str(x) for x in height_bits),2)
            except ValueError:
                breakpoint()
            tab_dec.append(np.uint8(dec))

        # tab_dec = [np.uint8(x) for x in tab_dec]
        tab_dec=np.asarray(tab_dec)
        
        img[:,:]=tab_dec.reshape([self.img_sz[0],self.img_sz[1] ])
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

    @property
    def can_read(self):
        """Ne pas utiliser dans la version module !!!!"""
        if self.ptr_tx > len(self.img_bin):
            return False
        return True

    # Step 3
    def __init__(self, img, secrecy_K):
        """
        Description : Constructeur du module

        Arguments : 
            img       => (np.array) image a transmettre
            secrecy_K => (int)      nombre de bits confidentiels
            src_sz    => (int)      taille de la source
        """
        
        self.name = "source"    # Set your module's name
        self.img    = img       # image a lire
        
        self.img_bin = self.img2bin()
        self.sec_sz = secrecy_K # nb de bits confidentiels
        self.img_sz = img.shape # taille de l'image
        
        self.ptr_tx = 0         # pointeur dans la sequence a lire
        self.ptx_rx = 0         # pointeur dans la sequence recue 