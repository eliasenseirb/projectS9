
import threading
import py_aff3ct as aff3ct
import pyaf
from myutils import weak_secrecy
from pyaf.splitter import Splitter
from pyaf.multiplexer import Multiplexer
from pyaf.padder import Padder
from source_nomod import Source
import numpy as np
from dvbs2_factory import dvbs2_factory

class Tx_class(threading.Thread):
    def __init__(self,threadID,name,params,params_bob,params_eve, src,path_file):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.params_bob = params_bob
        self.params_eve = params_eve
        self.src = src
        self.path_file = path_file
        self.K= params.K
        self.N= params.N
        self.p = params.p
        self.MODCOD = params.MODCOD
        self.n_frames = params.n_frames
        
        # -- CHAINE DE COM

        # -- -- BITS GELES
        # Ici, on compare les bits geles de Bob et de Eve
        # Le mode de decodage de Eve n'est pas pris en compte (sinon on ne pourrait
        # pas communiquer)
        # Cela permet de determiner un groupe de bits sur lesquels communiquer

        # Determination des bits geles de Bob
        fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(self.K,self.N)
        self.params_bob.noise = aff3ct.tools.noise.Sigma(self.params_bob.sigma)
        fbgen.set_noise(self.params_bob.noise)
        self.params_bob.frozen_bits = fbgen.generate()

        # Determination des bits geles de Eve
        self.params_eve.noise = aff3ct.tools.noise.Sigma(self.params_eve.sigma)
        fbgen.set_noise(self.params_eve.noise)
        self.params_eve.frozen_bits = fbgen.generate()


        # Determination des bits d'info et de leurs positions
        self.pos_mux_bits, self.N_mux_bits = weak_secrecy(self.params_bob, self.params_eve)
         
        
        """sec_K = count(mux_bits)         # nombre de bits utiles
        if sec_K == 0:
            self.error_msg.set("No secrecy channel available.\nPlease try with another SNR value.")
            return
        
        seq_pos = get_secrecy_position(self.params_bob.frozen_bits, pos_mux_bits)
        """
        

        # -- Src_rand
        # Permet de generer des sequences aleatoires pour
        # les bits random
        self.src_rand = aff3ct.module.source.Source_random_fast(self.K, 12)

        # -- Splitter (gets generated only once. Will be problematic if params change.)
        """
        if self.splt is None:
            splt = Splitter(self.src.img_bin, len(self.src.img_bin), sec_K)
            self.splt = splt
        else:
            self.rx_ptr = self.splt.get_rx_ptr()
            self.tx_ptr = self.splt.get_tx_ptr()
            splt = Splitter(self.src.img_bin, len(self.src.img_bin), sec_K)
            self.splt = splt
            splt.set_tx_ptr(self.tx_ptr)
            splt.set_rx_ptr(self.rx_ptr)
        """

        self.splt = Splitter(self.src.img_bin, len(self.src.img_bin), self.N_mux_bits,self.N_mux_bits)
        
        self.Fs = params.Fs      # fréquence d'echantillonnage
        self.Fc = params.Fc      # fréquence porteuse
        self.n_frames = params.n_frames  # nombre de trames
        self.MODCOD = params.MODCOD      # Type de modulation
        
        self.rad_params = pyaf.radio.USRP_params()
        self.rad_params.fifo_size  = 100
        self.rad_params.N          = 33480//2 
        self.rad_params.threaded   = True
        self.rad_params.tx_enabled = True
        self.rad_params.usrp_addr  = "type=b100"
        self.rad_params.tx_rate    = self.Fs
        self.rad_params.tx_antenna = "TX/RX"
        self.rad_params.tx_freq    = self.Fc
        self.rad_params.tx_gain    = 10

        self.rad      = pyaf.radio.Radio_USRP(self.rad_params)
        self.rad.n_frames = self.n_frames

        # -- padder
        self.sz_in  = (1,self.N)
        self.sz_out = (1,self.p)
        self.padder = pyaf.padder.Padder(self.sz_in[1], self.sz_out[1])
        self.pad_src = aff3ct.module.source.Source_random_fast(self.sz_out[1])
        
        # -- encoder
        self.enc = aff3ct.module.encoder.Encoder_polar_sys(self.K, self.N, self.params_bob.frozen_bits)

        # -- multiplexer
        self.mux = Multiplexer(self.pos_mux_bits, self.N_mux_bits, self.K)

        # -- modulator
        self.mdm = aff3ct.module.modem.Modem_BPSK_fast(self.p)

        # -- noise generator
        self.gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST

        # # -- channel
        self.chn = aff3ct.module.channel.Channel_AWGN_LLR(self.p, self.gen)

        # -- monitor
        mnt = aff3ct.module.monitor.Monitor_BFER_AR(self.N_mux_bits,1000,100)
        
        # -- framer-scrambler-shp_filter
        self.dvs2_factory = dvbs2_factory(self.MODCOD,file_path= self.path_file, n_frames=self.n_frames)
        self.framer                                    = self.dvs2_factory.framer_f                   .build()
        self.pl_scrambler                              = self.dvs2_factory.pl_scrambler_f             .build()
        self.shp_filter, mcd_filter                    = self.dvs2_factory.shaping_f                  .build()
        
        # -- gain
        self.N_chn_spls = 2*self.dvs2_factory.shaping_f.payload * self.dvs2_factory.shaping_f.oversampling_factor
        self.g = 0.5
        self.v = np.zeros((self.N_chn_spls,))
        self.v[0::2] = self.g
        self.gain = pyaf.multiplier.Multiplier_sequence_ccc(self.N_chn_spls,self.v,self.n_frames)
        

        # -- Sigma sockets
        self.sigma = np.ndarray(shape = (1,1), dtype=np.float32)
        self.sigma[0,0] = params.sigma

        # Chaîne TX
        self.mux [" multiplexer   :: good_bits "]   = self.splt["Split::bit_seq"]
        self.mux [" multiplexer    :: bad_bits "]   = self.src_rand["generate::U_K"]
        self.enc [" encode              :: U_K "]   = self.mux["multiplexer::sig_mux_out"]
        self.padder["padder        ::rand_bits "]   = self.pad_src["generate    ::U_K "]
        self.padder["padder        ::good_bits "]   = self.enc["encode     ::X_N "]
        self.padder["padder        ::sig_pad_out "] = self.mdm["modulate:: X_N1"]
        self.chn [" add_noise           :: X_N "]   = self.mdm["modulate:: X_N2"]
        self.framer          [   "generate::Y_N1"]  = self.chn [" add_noise           :: Y_N "]
        self.framer          [   "generate::Y_N2"]  = self.pl_scrambler    [   "scramble::X_N1"]
        self.shp_filter      [     "filter::X_N1"]  = self.pl_scrambler    [   "scramble::X_N2"]
        
        self.gain["imultiply::X_N"]     = self.shp_filter      [     "filter::Y_N2"] 
        self.rad   [       "send::X_N1"]= self.gain["imultiply::Z_N"]
        
        self.chn [" add_noise           ::  CP "] = self.sigma
        
        
        
        

        #sequ = aff3ct.tools.sequence.Sequence([splt["Split"],src_rand["generate"],pad_src["generate"]],1) # py_aff3ct.tools.sequence.Sequence
        self.seq = aff3ct.tools.sequence.Sequence([self.splt["Split"],self.src_rand["generate"],self.pad_src["generate"]],1)

    def run(self):
        self.alive=True
        while self.alive:        
            while not self.seq.is_done():
                self.seq.exec_step()
    def stop(self):
        self.alive=False