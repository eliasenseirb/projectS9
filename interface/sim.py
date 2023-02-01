"""

Demonstrator for the oral defense
Does not require radios

"""

import numpy as np
import sys, os
from dotenv import load_dotenv
from params import Bob, Eve

load_dotenv()

sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append(os.getenv("PYAF_PATH"))
sys.path.append("../src")

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc
import pyaf
from pyaf.splitter import Splitter
from pyaf.multiplexer import Multiplexer
from pyaf.mutualinformation import MutualInformation
from pyaf.padder import Padder
from myutils import weak_secrecy, gen_frozen, display_frozen_bits, display_common_frozen_bits

class Sim:
    """
    Instantiates the simulation part for the demonstrator
    """

    def __init__(self, img, ebn0=12, decoder="Bob", Eve_has_mux=False, secrecy="weak"):
        """Create the simulation"""
        self.ebn0 = ebn0
        self.params_bob = Bob(ebn0)
        self.params_eve = Eve(ebn0, has_mux=Eve_has_mux)
        self.has_mux = Eve_has_mux
        # Setup for weak secrecy
        if secrecy=='weak':
            self.sec_pos, self.sec_sz = weak_secrecy(self.params_bob, self.params_eve)
        # Setup for no secrecy
        else:
            gen_frozen(self.params_bob, self.params_eve)
            self.sec_pos = np.arange(1,self.params_bob.K+1).tolist()
            
            self.sec_sz = self.params_bob.K
        self.decoder_type = decoder
        
        
        self.img = img

    @property
    def sequence(self):
        s = self._create_sequence()
        return s
         
    def _create_sequence(self):
        """Create the py_aff3ct sequence"""

        self._create_Tx()
        
        self._create_channel()

        self._create_Rx()

        s = self._bind_all()
        
        return s

    def _bind_all(self):
        """Link all the sockets together"""
        Tx_splt, Tx_src, Tx_mux, Tx_enc, Tx_mdm = self.Tx
        Rx_mdm, Rx_dec, Rx_mux, Rx_sigma, Rx_mui, Rx_splt, Rx_mnt = self.Rx
        chn = self.chn
        
        # Transmitter
        Tx_mux [" multiplexer   :: good_bits "] = Tx_splt["Split::bit_seq"]
        Tx_mux [" multiplexer    :: bad_bits "] = Tx_src["generate::U_K"]
        Tx_enc [" encode              :: U_K "] = Tx_mux["multiplexer::sig_mux_out"]
        Tx_mdm [" modulate            :: X_N1"] = Tx_enc["encode::X_N"]
        
        chn    [" add_noise           :: X_N "] = Tx_mdm["modulate::X_N2"]
        
        # Receiver
        # Either Bob or Eve
        Rx_mdm [" demodulate          :: Y_N1"] = chn["add_noise::Y_N"]
        Rx_dec [" decode_siho         :: Y_N "] = Rx_mdm["demodulate::Y_N2"]

        # In the specific case where Eve has no demux module
        # the splitter module gets every bit received (good and noise)
        # The mux is still included but after the splitter so that one can
        # compute the mutual information and BER without it affecting the image
        # display
        if self.decoder_type=="Eve" and not self.has_mux:
            Rx_splt["Collect :: buffer"] = Rx_dec ["decode_siho:: V_K"]
            Rx_mux["demultiplexer::mux_sequence"] = Rx_splt["Collect::through"]
            Rx_mui["compute::rx"] = Rx_mux["demultiplexer::good_bits"]
        else:
            Rx_mux["demultiplexer::mux_sequence"] = Rx_dec["decode_siho::V_K"]
            Rx_splt[" Collect           :: buffer"] = Rx_mux["demultiplexer::good_bits"]
            Rx_mui [" compute             ::  rx "] = Rx_splt["Collect::through"]
        

        Rx_mnt [" check_errors        ::   U "] = Tx_splt["Split::bit_seq"]
        Rx_mui [" compute             :: src "] = Tx_splt["Split::bit_seq"]
        Rx_mnt [" check_errors        ::   V "] = Rx_mui ["compute::through"]
        chn    [" add_noise           ::  CP "] = Rx_sigma
        Rx_mdm [" demodulate          ::  CP "] = Rx_sigma

        return aff3ct.tools.sequence.Sequence([Tx_splt["Split"], Tx_src["generate"]], 1)

    def _create_Tx(self):
        """Create Alice's modules"""
        # -- Splitter
        splt = Splitter(self.img, len(self.img), self.sec_sz, self.sec_sz)

        # -- Random source
        src = aff3ct.module.source.Source_random_fast(self.params_bob.K)
        
        # -- Encoder
        enc = aff3ct.module.encoder.Encoder_polar_sys(self.params_bob.K, self.params_bob.N, self.params_bob.frozen_bits)

        # -- Multiplexer
        mux = Multiplexer(self.sec_pos, self.sec_sz, self.params_bob.K)
        
        # -- Modulator
        mdm = aff3ct.module.modem.Modem_BPSK_fast(self.params_bob.N)
        
        self.Tx = [splt, src, mux, enc, mdm]

    def _create_channel(self):
        """Create the gaussian channel"""
        # -- Noise generator
        gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST

        # -- Channel
        chn = aff3ct.module.channel.Channel_AWGN_LLR(self.params_bob.N, gen)

        self.chn = chn

    def _create_Rx(self):
        """Create Bob's or Eve's receiver sequence"""
        
        # Receiver choice
        if self.decoder_type == "Bob":
            params = self.params_bob
        else:
            params = self.params_eve

        # -- Modulator
        mdm = aff3ct.module.modem.Modem_BPSK_fast(params.N)

        # -- Decoder
        dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(self.params_bob.K, self.params_bob.N, self.params_bob.frozen_bits)
        
        if self.decoder_type == "Bob" or self.params_eve.has_mux:
            # -- Demultiplexer
            mux = Multiplexer(self.sec_pos, self.sec_sz, self.params_bob.K)
            splt = Splitter(self.img, len(self.img), self.sec_sz, self.sec_sz)
            
        else:
            mux = Multiplexer(self.sec_pos, self.sec_sz, self.params_bob.K)
            splt = Splitter(self.img, len(self.img), self.params_bob.K, self.params_bob.K)
            
        mui = MutualInformation(self.sec_sz)
        mnt = aff3ct.module.monitor.Monitor_BFER_AR(self.sec_sz, 1000, 100)
       

        # -- Sigma socket
        sigma = np.ndarray(shape = (1,1), dtype=np.float32)
        sigma[0,0] = params.sigma
        print(f"{params.sigma}")
        self.Rx = [mdm, dec, mux, sigma, mui, splt, mnt]


    def update(self, ebn0=12, decoder="Bob", Eve_has_mux=False, secrecy='weak'):
        """Update parameters if needed"""
        if self.ebn0 != ebn0:
            self.params_bob = Bob(ebn0)
            self.params_eve = Eve(ebn0, Eve_has_mux)
            # Setup weak secrecy
            if secrecy=='weak':
                self.sec_pos, self.sec_sz = weak_secrecy(self.params_bob, self.params_eve)
            # Setup for no secrecy
            else:
                self.sec_pos = np.arange(1,self.params_bob.K+1).tolist
                self.sec_sz = self.params_bob.K
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

    @property
    def stats(self):
        t = (self.Rx[-1].get_ber(), self.Rx[-3].get_mui())
        self.Rx[-1].reset()
        return t
    
    @property
    def N(self):
        return self.sec_sz