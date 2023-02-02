"""

Transmitter version of the GUI

"""

import tkinter as tk
import tkinter.filedialog as fd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np 
import sys
import os
from dotenv import load_dotenv
import time
import math
import matplotlib.pyplot as plt
import cv2

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append(os.getenv("PYAF_PATH"))
sys.path.append(os.getenv("THREADED_PATH"))
sys.path.append("../src")
sys.path.append("..")

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc
import pyaf
import threaded_sequence
from pyaf.splitter import Splitter
from pyaf.multiplexer import Multiplexer
from pyaf.padder import Padder
from source_nomod import Source
from frozenbits_handler import all_no, no, get_secrecy_position, count, weak_secrecy
from params import Bob, Eve
from dvbs2_factory import dvbs2_factory


class App(tk.Tk):

    def open_file(self):
        """Prompt the user to select a file and store its path"""
        # Open a file selection dialog
        self.path_file = fd.askopenfilename()
        self.file_text_var.set(self.path_file.split("/")[-1])
        self.img =cv2.imread(self.path_file)[:,:,0] # image grayscale
        self.img_shape = self.img.shape
        
        self.img_rx = np.ndarray(shape=self.img_shape, dtype=np.uint8)

        # -- Source
        # Converts the grayscale image into a bin sequence
        self.src = Source(self.img, 1)

    def start(self):
        """Run the simulation"""
        self.error_msg.set("")
        self.run_simulation()

    def stop(self):
        """Stop the simulation"""
        self.error_msg.set("Simulation stopped.")
        self.left_frame.after_cancel(self._job)

    def format_img(self, img, img_shape) -> np.ndarray :
        """Transform an int list into np.uint8"""
        if len(img) != 8*img_shape[0]*img_shape[1]:
            raise ValueError(f"Erreur ! La taille de la liste {len(img)} ne correspond pas au format d'image ({img_shape[0]}, {img_shape[1]})")

        img_uint8 = [np.uint8(x) for x in img]
        img_reshaped = np.reshape(img_uint8, img_shape)

        return img_reshaped
    
    def update_top_img(self):
        """Update the top plot"""
        self.top_plot.imshow(self.img_rx, cmap='gist_gray')
        self.top_plot.set_xlabel('pixels')
        self.top_plot.set_ylabel('pixels')
        self.top_canvas.draw()
        self.top_canvas.flush_events()

    def clear_img(self):
        """Replace the image with an empty plot"""
        img_vide = np.zeros((2,2), dtype=int)
        self.top_plot.imshow(img_vide, cmap='gist_gray')
        self.top_plot.set_xlabel('')
        self.top_plot.set_ylabel('')
        self.top_canvas.draw()
    
    def stop_simu(self):
        """Stop transmitting"""
        self.stop_flag = 0

    def select_decoder(self):
        """Select the polar decoder used"""
        K = int(self.k_var.get())  # replace with desired value
        N = int(self.n_var.get())  # replace with desired value
        
        fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K,N)
        noise = aff3ct.tools.noise.Sigma(self.sigma)
        fbgen.set_noise(noise)
        frozen_bits = fbgen.generate()

        # Decoder choice
        decoder = self.decoder.get()
        if decoder == 'sc_fast':
            dec = aff3ct.module.decoder.Decoder_polar_SC_fast_sys(K, N, frozen_bits)
        elif decoder == 'sc_naive':
            dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(K, N, frozen_bits)
        else:
            # use other decoder
            dec = aff3ct.module.decoder.Decoder_other(K, N, frozen_bits)
        return dec


    def tx_start(self):
        """Start transmitting data"""
        self.stop_flag = 1

        if(self.path_file == ''):
            self.error_msg.set("No image selected.")
            return

        if(self.decoder.get() == ''):
            self.error_msg.set("No decoder selected.")
            return
    
        if(self.secrecy_mode.get() == ''):
            self.error_msg.set("No secrecy selected.")
            return

        dec_choice = self.decoder_choice.get()

        params = self.params_case[dec_choice]
        
        
        K = self.params_bob.K # Input size of the polar encoder
        N = params.N          # Output size of the polar encoder
        p = params.p          # Output size of the padder
        ebn0 = params.ebn0    # SNR

        esn0 = ebn0 + 10*math.log10(K/N)
        sigma_val = 1/(math.sqrt(2)*10**(esn0/20))


        # -- CHAINE DE COM

        # -- FROZEN BITS
        # The following lines compare the bits that should be
        # frozen for both Bob and Eve, based on their SNR.
        # This allows to detect the channels on which
        # Eve has a bad decoding power, and thus on which
        # she will make the most errors when decoding.

        # Bob's frozen bits
        fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K,N)
        self.params_bob.noise = aff3ct.tools.noise.Sigma(self.params_bob.sigma)
        fbgen.set_noise(self.params_bob.noise)
        self.params_bob.frozen_bits = fbgen.generate()

        # Eve's frozen bits
        self.params_eve.noise = aff3ct.tools.noise.Sigma(self.params_eve.sigma)
        fbgen.set_noise(self.params_eve.noise)
        self.params_eve.frozen_bits = fbgen.generate()


        # Determination of the weak secrecy channels
        pos_mux_bits, N_mux_bits = weak_secrecy(self.params_bob, self.params_eve)
         
        
        """sec_K = count(mux_bits)         # nombre de bits utiles
        if sec_K == 0:
            self.error_msg.set("No secrecy channel available.\nPlease try with another SNR value.")
            return
        
        seq_pos = get_secrecy_position(self.params_bob.frozen_bits, pos_mux_bits)
        """
        

        # -- Src_rand
        # Generates a random stream of bits
        src_rand = aff3ct.module.source.Source_random_fast(K, 12)

        # -- Splitter
        splt = Splitter(self.src.img_bin, len(self.src.img_bin), N_mux_bits,N_mux_bits)
        
        Fs = params.Fs      # Sampling frequency
        Fc = params.Fc      # Carrier frequency
        n_frames = params.n_frames  # Number of frames
        MODCOD = params.MODCOD      # Modulation type
        
        # -- Radio parameters
        rad_params = pyaf.radio.USRP_params()
        rad_params.fifo_size  = 100
        rad_params.N          = 33480//2 
        rad_params.threaded   = True
        rad_params.tx_enabled = True
        rad_params.usrp_addr  = "type=b100"
        rad_params.tx_rate    = Fs
        rad_params.tx_antenna = "TX/RX"
        rad_params.tx_freq    = Fc
        rad_params.tx_gain    = 10

        rad      = pyaf.radio.Radio_USRP(rad_params)
        rad.n_frames = n_frames

        # -- Padder
        sz_in  = (1,N)
        sz_out = (1,p)
        padder = pyaf.padder.Padder(sz_in[1], sz_out[1])
        pad_src = aff3ct.module.source.Source_random_fast(sz_out[1])
        
        # -- Encoder
        enc = aff3ct.module.encoder.Encoder_polar_sys(K, N, self.params_bob.frozen_bits)

        # -- Multiplexer        
        mux = Multiplexer(pos_mux_bits, N_mux_bits, K)
        
        # -- Modulator
        mdm = aff3ct.module.modem.Modem_BPSK_fast(p)

        # -- Noise generator
        gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST

        # -- Channel
        chn = aff3ct.module.channel.Channel_AWGN_LLR(p, gen)

        # -- Monitor
        mnt = aff3ct.module.monitor.Monitor_BFER_AR(N_mux_bits,1000,100)
        
        # -- Framer-scrambler-shp_filter
        dvs2_factory = dvbs2_factory(MODCOD,file_path= self.path_file, n_frames=n_frames)
        framer                                    = dvs2_factory.framer_f                   .build()
        pl_scrambler                              = dvs2_factory.pl_scrambler_f             .build()
        shp_filter, mcd_filter                    = dvs2_factory.shaping_f                  .build()
        
        # -- Gain
        N_chn_spls = 2*dvs2_factory.shaping_f.payload * dvs2_factory.shaping_f.oversampling_factor
        g = 0.5
        v = np.zeros((N_chn_spls,))
        v[0::2] = g
        gain = pyaf.multiplier.Multiplier_sequence_ccc(N_chn_spls,v,n_frames)
        

        # -- Sigma sockets
        sigma = np.ndarray(shape = (1,1), dtype=np.float32)
        sigma[0,0] = 0.0005

        # Chaîne TX
        mux [" multiplexer   :: good_bits "] = splt["Split::bit_seq"]
        mux [" multiplexer    :: bad_bits "] = src_rand["generate::U_K"]
        enc [" encode              :: U_K "] = mux["multiplexer::sig_mux_out"]
        padder["padder        ::rand_bits "] = pad_src["generate    ::U_K "]
        padder["padder        ::good_bits "] = enc["encode     ::X_N "]
        padder["padder        ::sig_pad_out "] = mdm["modulate:: X_N1"]
        chn [" add_noise           :: X_N "]= mdm["modulate:: X_N2"]
        framer          [   "generate::Y_N1"] = chn [" add_noise           :: Y_N "]
        framer          [   "generate::Y_N2"] = pl_scrambler    [   "scramble::X_N1"]
        shp_filter      [     "filter::X_N1"] = pl_scrambler    [   "scramble::X_N2"]
        
        #framer          [   "generate::Y_N2"] = shp_filter      [     "filter::X_N1"]
        
        gain["imultiply::X_N"] = shp_filter      [     "filter::Y_N2"] 
        rad   [       "send::X_N1"]= gain["imultiply::Z_N"]
        
        chn [" add_noise           ::  CP "] = sigma
        
        self.seq = aff3ct.tools.sequence.Sequence([splt["Split"],src_rand["generate"],pad_src["generate"]],1)

        while self.stop_flag:
            
            while not self.seq.is_done():
                self.seq.exec_step()
            

    def __init__(self):
        """Constructor.
        Setup the different buttons for the GUI
        """
        tk.Tk.__init__(self)

        self.path_file = ""
        self.title("Pol'eirb Codes")
        self.geometry("1080x720")
        self.minsize(width=720, height=480)

        # Set up the left frame with the parameters
        self.left_frame = tk.LabelFrame(self, text="Parameters")
        self.left_frame.pack(side="left", fill="both", expand=True)

        # SNR values slider
        # Values go from -4 to 30
        # the variable to access it is self.snr_slider
    
        self.snr_label = tk.Label(self.left_frame, text="SNR values:")
        self.snr_label.pack()
        self.snr_slider = tk.Scale(self.left_frame, from_=-4, to=30, orient="horizontal")
        self.snr_slider.pack()
        self.snr_slider.set(5)

        self.inv_label = tk.Label(self.left_frame)
        self.inv_label.pack()

        # Decoders radio buttons
        # Decoder can either be SC_Fast or SC_Naive

        self.decoder_label = tk.Label(self.left_frame, text="Encoder:")
        self.decoder_label.pack()
        self.decoder = tk.StringVar(self.left_frame)
        self.decoder.set('') 
        self.sc_fast_button = tk.Radiobutton(self.left_frame, text='SC Fast', variable=self.decoder, value='sc_fast') 
        self.sc_fast_button.pack() 
        self.sc_naive_button = tk.Radiobutton(self.left_frame, text='SC Naive', variable=self.decoder, value='sc_naive') 
        self.sc_naive_button.pack() 
        self.other_button = tk.Radiobutton(self.left_frame, text='Other', variable=self.decoder, value='other') 
        self.other_button.pack()
        self.sc_naive_button.select()

        # Secrecy mode radio buttons
        # Allow to choose between weak secrecy and strong secrecy
        # this one is for future use, since strong secrecy is not
        # implemented.

        self.secrecy_mode_label = tk.Label(self.left_frame, text="Secrecy mode:")
        self.secrecy_mode_label.pack()
        self.secrecy_mode = tk.StringVar(self.left_frame)
        self.secrecy_mode.set('') 
        self.weak_button = tk.Radiobutton(self.left_frame, text='Weak', variable=self.secrecy_mode, value='weak') 
        self.weak_button.pack() 
        self.strong_button = tk.Radiobutton(self.left_frame, text='Strong', variable=self.secrecy_mode, value='strong') 
        self.strong_button.pack() 
        self.weak_button.select()

        self.inv_label6 = tk.Label(self.left_frame)
        self.inv_label6.pack()

        # Decoder choice
        # Three choices can be made here
        #  Bob Decoder: Use Bob's frozen bits, and no degradation
        #  for the SNR
        #  Eve's Decoder (Bob fb): Use Eve's decoder (degraded)
        #  bot Bob's fb
        #  Eve's Decoder (Eve fb): Use both Eve's decoder (degraded)
        #  and Eve's fb (demonstrates weak secrecy)

        self.decoder_choice = tk.StringVar()
        self.decoder_choice_str = tk.Label(self.left_frame, text="Receiver:")

        self.decoder_choice_bob   = tk.Radiobutton(self.left_frame, text="Bob", variable = self.decoder_choice, value = "Bob")
        self.decoder_choice_eve01 = tk.Radiobutton(self.left_frame, text="Eve (no secrecy)", variable = self.decoder_choice, value = "Eve01")
        self.decoder_choice_eve02 = tk.Radiobutton(self.left_frame, text="Eve (secrecy)", variable = self.decoder_choice, value = "Eve02")

        self.decoder_choice_str.pack()
        self.decoder_choice_bob.pack()
        self.decoder_choice_eve01.pack()
        self.decoder_choice_eve02.pack()

        self.decoder_choice_bob.select()

        # File input button
        # Allow to fetch an image file on the disk and
        # save its path locally.
        # Then it can be loaded in the simulation

        self.file_button = tk.Button(self.left_frame, text="Select image", command=self.open_file)
        self.file_text_var = tk.StringVar()
        self.file_text_var.set("No image loaded.")
        self.file_text = tk.Label(self.left_frame, textvariable=self.file_text_var)
        self.file_button.pack(pady=10)
        self.file_text.pack()

        # Simulation button test

        self.simulation_button = tk.Button(self.left_frame, text="Run simulation", command=self.tx_start)
        self.simulation_button.pack(pady=5)

        # Clear button
        self.clear_button = tk.Button(self.left_frame, text="Clear Image", command=self.clear_img)
        self.clear_button.pack(pady=5)

        # Clear button
        self.stop_simu_button = tk.Button(self.left_frame, text="Stop Simulation", command=self.stop_simu)
        self.stop_simu_button.pack(pady=5)

        # Error messages
        # Allows for error messages display during the simulation
        self.error_msg    = tk.StringVar()
        self.error_msg.set ("")
        self.error_output = tk.Label(self.left_frame, textvariable=self.error_msg, fg='#ff0000')

        self.error_output.pack()

        # Set up the right frame with the plots
        self.right_frame = tk.LabelFrame(self, text="Figures")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Set up the upper frame for the scatterplot
        self.upper_frame = tk.LabelFrame(self.right_frame, text="Image received")
        self.upper_frame.pack(side="top", fill="both", expand=True)

     
        self.top_figure = Figure() 
        self.top_plot = self.top_figure.add_subplot(111) 
        self.top_canvas = FigureCanvasTkAgg(self.top_figure, self.upper_frame) 
        self.top_canvas.draw() 
        self.top_canvas.get_tk_widget().pack(side='top', fill='both', expand=True) 
 
       
        self.splt = None
        self.params_bob = Bob(self.snr_slider.get())
        self.params_eve = Eve(self.snr_slider.get())

        # pseudo-switch case statement for Python
        # For compatibility with versions 3.7, 3.8 and 3.9
        self.params_case = {
            "Bob"   : self.params_bob,
            "Eve01" : self.params_eve,
            "Eve02" : self.params_eve
        }

        self.ptr_rx = 0
        self.ptr_tx = 0
        self.error_rate = np.ndarray((1,10000), dtype=float)
        self.time_axis = np.arange(1,10001)
        self.error_rate_idx = 0

app = App()
app.bind('<Escape>', lambda e: close_win(e))

def close_win(e):
    app.destroy()

app.mainloop()



