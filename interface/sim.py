import numpy as np
import sys, os
from dotenv import load_dotenv
from params import Bob, Eve

load_dotenv()

sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append("../"+os.getenv("AFF3CT_PATH"))
sys.path.append(os.getenv("PYAF_PATH"))
sys.path.append("../"+os.getenv("PYAF_PATH"))

sys.path.append("../src")

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc
import pyaf
from pyaf.splitter import Splitter
from pyaf.multiplexer import Multiplexer
from pyaf.mutualinformation import MutualInformation
from pyaf.padder import Padder
from myutils import weak_secrecy

class Sim:
    """
    Instantie toute la partie simulation du demonstrateur
    Afin de liberer de la place dans le fichier interface.py

    L'objet Sim doit pouvoir generer toute la simulation a partir
    des donnees fournies par l'interface.
    """

    def __init__(self, img, ebn0=12, decoder="Bob"):
        """Cree la simulation"""
        self.ebn0 = ebn0
        self.params_bob = Bob(ebn0)
        self.params_eve = Eve(ebn0)
        self.sec_pos, self.sec_sz = weak_secrecy(self.params_bob, self.params_eve)
        self.decoder_type = decoder
        self.img = img

    @property
    def sequence(self):
        s = self._create_sequence()
        return s
        
        
        
    
    def _create_sequence(self):
        """Instantie la sequence pyaff3ct"""

        self._create_Tx()
        
        self._create_channel()

        self._create_Rx()

        s = self._bind_all()
        
        return s

    def _bind_all(self):
        Tx_splt, Tx_src, Tx_mux, Tx_enc, Tx_mdm = self.Tx
        Rx_mdm, Rx_dec, Rx_mux, Rx_sigma, Rx_pad, Rx_zeros, Rx_mui, Rx_splt, Rx_mnt = self.Rx
        chn = self.chn
        
        # Emetteur
        # Alice : invariant
        Tx_mux [" multiplexer   :: good_bits "] = Tx_splt["Split::bit_seq"]
        Tx_mux [" multiplexer    :: bad_bits "] = Tx_src["generate::U_K"]
        Tx_enc [" encode              :: U_K "] = Tx_mux["multiplexer::sig_mux_out"]
        Tx_mdm [" modulate            :: X_N1"] = Tx_enc["encode::X_N"]
        
        chn    [" add_noise           :: X_N "] = Tx_mdm["modulate::X_N2"]
        
        # Recepteur
        # Bob ou Eve
        # Le cas ou aucun demultiplexeur n'est fourni est pris en compte
        Rx_mdm [" demodulate          :: Y_N1"] = chn["add_noise::Y_N"]
        Rx_dec [" decode_siho         :: Y_N "] = Rx_mdm["demodulate::Y_N2"]
        if Rx_mux is None:
            Rx_splt["Collect :: buffer"] = Rx_dec ["decode_siho:: V_K"]
        else:
            Rx_mux["demultiplexer::mux_sequence"] = Rx_dec["decode_siho::V_K"]
            Rx_splt[" Collect           :: buffer"] = Rx_mux["demultiplexer::good_bits"]
        """
        else:
            Rx_pad["padder::good_bits"] = Rx_dec["decode_siho::V_K"]
            Rx_pad["padder::rand_bits"] = Rx_zeros
            Rx_mux["demultiplexer::mux_sequence"] = Rx_pad["padder::sig_pad_out"]
        """

        Rx_mnt [" check_errors        ::   U "] = Tx_splt["Split::bit_seq"]
        Rx_mui [" compute             :: src "] = Tx_splt["Split::bit_seq"]
        Rx_mui [" compute             ::  rx "] = Rx_splt["Collect::through"]
        Rx_mnt [" check_errors        ::   V "] = Rx_mui ["compute::through"]
        chn    [" add_noise           ::  CP "] = Rx_sigma
        Rx_mdm [" demodulate          ::  CP "] = Rx_sigma

        

        return aff3ct.tools.sequence.Sequence(Tx_splt["Split"], Rx_mnt["check_errors"], 1)

    def _create_Tx(self):

        # -- Splitter
        splt = Splitter(self.img, len(self.img), self.sec_sz, self.sec_sz)

        # -- random source
        src = aff3ct.module.source.Source_random_fast(self.params_bob.K, 12)
        
        # -- encoder
        enc = aff3ct.module.encoder.Encoder_polar_sys(self.params_bob.K, self.params_bob.N, self.params_bob.frozen_bits)

        # -- mux
        mux = Multiplexer(self.sec_pos, self.sec_sz, self.params_bob.K)
        
        # -- modulateur
        mdm = aff3ct.module.modem.Modem_BPSK_fast(self.params_bob.N)
        
        self.Tx = [splt, src, mux, enc, mdm]

    def _create_channel(self):

        # -- noise generator
        gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST

        # -- channel
        chn = aff3ct.module.channel.Channel_AWGN_LLR(self.params_bob.N, gen)

        self.chn = chn

    def _create_Rx(self):

        # choix du recepteur
        if self.decoder_type == "Bob":
            params = self.params_bob
        else:
            params = self.params_eve

        # -- modulateur
        mdm = aff3ct.module.modem.Modem_BPSK_fast(params.N)

        # -- decodeur
        dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(params.K, params.N, params.frozen_bits)

        # -- demux
        if self.decoder_type == "Bob":
            # Bob a toujours un decodeur
            # Eve n'en a un que si on lui specifie
            
            
            mux = Multiplexer(self.sec_pos, self.sec_sz, self.params_bob.K)
            pad = None
            zeros = None
            splt = Splitter(self.img, len(self.img), self.sec_sz, self.sec_sz)
            mui = MutualInformation(self.sec_sz)
            mnt = aff3ct.module.monitor.Monitor_BFER_AR(self.sec_sz, 1000, 100)
        else:
            
            mux = None
            zeros = None
            pad = None
            splt = Splitter(self.img, len(self.img), params.K, self.sec_sz)
            mui = MutualInformation(self.sec_sz)
            mnt = aff3ct.module.monitor.Monitor_BFER_AR(self.sec_sz,1000,100)

            # limitation des donnees lues (evite de traiter le padding)
            splt.set_limit_rx(self.sec_sz)
            #mui.set_limit(params.K)
        

        # -- Sigma socket
        sigma = np.ndarray(shape = (1,1), dtype=np.float32)
        sigma[0,0] = params.sigma

        self.Rx = [mdm, dec, mux, sigma, pad, zeros, mui, splt, mnt]


    def update(self, ebn0, decoder, Eve_has_mux):
        """Update parameters if needed"""
        if self.ebn0 != ebn0:
            self.params_bob = Bob(ebn0)
            self.params_eve = Eve(ebn0, Eve_has_mux)
            self.sec_pos, self.sec_sz = weak_secrecy(self.params_bob, self.params_eve)
        self.decoder_type = decoder

    @property
    def rx(self):
        return self.Rx[-2].get_rx()

    @property
    def ber(self):
        t = self.Rx[-1].get_ber()
        self.Rx[-1].reset()
        return t

    @property
    def mui(self):
        self.Rx[-1].reset()
        return self.Rx[-3].get_mui()