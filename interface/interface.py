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
sys.path.append("../"+os.getenv("AFF3CT_PATH"))
sys.path.append(os.getenv("PYAF_PATH"))
sys.path.append("../"+os.getenv("PYAF_PATH"))

sys.path.append("../src")

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc
import pyaf
from pyaf.splitter import Splitter
from pyaf.multiplexer import Multiplexer
from source_nomod import Source
from myutils import all_no, no, get_secrecy_position, count
from params import Bob, Eve

class App(tk.Tk):
    

    def open_file(self):
        # Open a file selection dialog
        self.path_file = fd.askopenfilename()
        self.file_text_var.set(self.path_file.split("/")[-1])
        self.img =cv2.imread(self.path_file)[:,:,0] # image grayscale
        self.img_shape = self.img.shape
        
        self.img_rx = np.ndarray(shape=self.img_shape, dtype=np.uint8)

        # -- Source
        # Permet de convertir l'image en sequence binaire
        self.src = Source(self.img, 1)


    def start(self):
        self.error_msg.set("")
        self.run_simulation()

    def stop(self):
        self.error_msg.set("Simulation stopped.")
        self.left_frame.after_cancel(self._job)

    def format_img(self, img: list[int], img_shape: tuple[int, int]) -> np.ndarray :
        """Transforme une liste d'entiers en tableau numpy d'uint8"""
        if len(img) != 8*img_shape[0]*img_shape[1]:
            raise ValueError(f"Erreur ! La taille de la liste {len(img)} ne correspond pas au format d'image ({img_shape[0]}, {img_shape[1]})")

        img_uint8 = [np.uint8(x) for x in img]
        img_reshaped = np.reshape(img_uint8, img_shape)

        return img_reshaped
    
    def update_top_img(self):
        self.top_plot.imshow(self.img_rx, cmap='gist_gray')
        self.top_plot.set_xlabel('pixels')
        self.top_plot.set_ylabel('pixels')
        self.top_canvas.draw()
        self.top_canvas.flush_events()

    def update_bottom_plot(self):

        if self.error_rate_idx > 10:
            left  = self.error_rate_idx-10
            right = self.error_rate_idx
        else:
            left  = 0 
            right = 10

        self.bottom_plot.cla()
        slg = self.bottom_plot.plot(self.time_axis, self.error_rate[0,:])
        self.bottom_plot.set_xlim(left, right)
        self.bottom_plot.set_ylim(0.00001,1)
        self.bottom_plot.set_title("BER")
        self.bottom_plot.set_xlabel("Time")
        self.bottom_plot.set_ylabel("ber")
        self.bottom_canvas.draw()

    def clear_img(self):
        img_vide = np.zeros((2,2), dtype=int)
        self.top_plot.imshow(img_vide, cmap='gist_gray')
        self.top_plot.set_xlabel('')
        self.top_plot.set_ylabel('')
        self.top_canvas.draw()
    
    def stop_simu(self):
        self.stop_flag = 0

    def select_decoder(self):
        K = int(self.k_var.get())  # replace with desired value
        N = int(self.n_var.get())  # replace with desired value
        
        fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K,N)
        noise = aff3ct.tools.noise.Sigma(self.sigma)
        fbgen.set_noise(noise)
        frozen_bits = fbgen.generate()

        #retirer les "" pour affilier la bonne valeur au décodeur
        decoder = self.decoder.get()
        if decoder == 'sc_fast':
            dec = aff3ct.module.decoder.Decoder_polar_SC_fast_sys(K, N, frozen_bits)
        elif decoder == 'sc_naive':
            dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(K, N, frozen_bits)
        else:
            # use other decoder
            dec = aff3ct.module.decoder.Decoder_other(K, N, frozen_bits)
        return dec


    def run_sim_alex(self):
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
        
        
        K = self.params_bob.K        # taille a l'entree de l'encodeur
        N = params.N        # taille a la sortie de l'encodeur
        ebn0 = params.ebn0  # SNR

        esn0 = ebn0 + 10*math.log10(K/N)
        sigma_val = 1/(math.sqrt(2)*10**(esn0/20))


        

        # -- CHAINE DE COM

        # -- -- BITS GELES
        # Ici, on compare les bits geles de Bob et de Eve
        # Le mode de decodage de Eve n'est pas pris en compte (sinon on ne pourrait
        # pas communiquer)
        # Cela permet de determiner un groupe de bits sur lesquels communiquer

        # Determination des bits geles de Bob
        fbgen_bob = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(self.params_bob.K,self.params_bob.N)
        self.params_bob.noise = aff3ct.tools.noise.Sigma(self.params_bob.sigma)
        fbgen_bob.set_noise(self.params_bob.noise)
        self.params_bob.frozen_bits = fbgen_bob.generate()

        # Determination des bits geles de Eve
        fbgen_eve = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(self.params_eve.K,self.params_eve.N)
        self.params_eve.noise = aff3ct.tools.noise.Sigma(self.params_eve.sigma)
        fbgen_eve.set_noise(self.params_eve.noise)
        self.params_eve.frozen_bits = fbgen_eve.generate()


        # Determination des bits d'info et de leurs positions
        mux_bits, pos_mux_bits = all_no(self.params_bob.frozen_bits, self.params_eve.frozen_bits)
        
        sec_K = count(mux_bits)         # nombre de bits utiles
        
        self.error_msg.set(f"Bits confidentiels: {sec_K}")
        if sec_K == 0:
            self.error_msg.set("No secrecy channel available.\nPlease try with another SNR value.")
            return
        
        seq_pos = get_secrecy_position(self.params_bob.frozen_bits, pos_mux_bits)

        

        # -- Src_rand
        # Permet de generer des sequences aleatoires pour
        # les bits random
        src_rand = aff3ct.module.source.Source_random_fast(self.params_bob.K, 12)

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

        splt = Splitter(self.src.img_bin, len(self.src.img_bin), sec_K)

        # -- encoder
        enc = aff3ct.module.encoder.Encoder_polar_sys(self.params_bob.K, self.params_bob.N, self.params_bob.frozen_bits)

        # -- multiplexer
        mux_bob = Multiplexer(seq_pos, count(mux_bits), self.params_bob.K)
        mux_eve = Multiplexer(seq_pos, count(mux_bits), self.params_eve.K)

        if dec_choice == "Bob":
            mux = mux_bob
        else:
            mux = mux_eve
        # -- decoder
        # params.frozen_bits s'adapte a la simulation demandee
        # S'il s'agit de Bob ou d'Eve sans confidentialite, 
        # les bits geles de Bob sont utilises
        # Sinon, les bits geles de Eve sont utilises
        
        if dec_choice == "Eve01":
            params.frozen_bits = self.params_bob.frozen_bits
        
        dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(params.K, self.params_bob.N, params.frozen_bits)

        # -- modulator
        mdm = aff3ct.module.modem.Modem_BPSK_fast(N)

        # -- noise generator
        gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST

        # -- channel
        chn = aff3ct.module.channel.Channel_AWGN_LLR(N, gen)

        # -- monitor
        mnt = aff3ct.module.monitor.Monitor_BFER_AR(sec_K,1000,100)

        # -- Sigma sockets
        self.sigma = np.ndarray(shape = (1,1), dtype=np.float32)
        self.sigma[0,0] = params.sigma

        mux_bob [" multiplexer   :: good_bits "] = splt["Split::bit_seq"]
        mux_bob [" multiplexer    :: bad_bits "] = src_rand["generate::U_K"]
        enc [" encode              :: U_K "] = mux_bob["multiplexer::sig_mux_out"]
        mdm [" modulate            :: X_N1"] = enc["encode::X_N"]
        chn [" add_noise           :: X_N "] = mdm["modulate::X_N2"]
        mdm [" demodulate          :: Y_N1"] = chn["add_noise::Y_N"]
        dec [" decode_siho         :: Y_N "] = mdm["demodulate::Y_N2"]
        mux [" demultiplexer::mux_sequence"] = dec["decode_siho::V_K"] 
        splt[" Collect           :: buffer"] = mux["demultiplexer::good_bits"]
        mnt [" check_errors        ::   U "] = splt["Split::bit_seq"]
        mnt [" check_errors        ::   V "] = splt["Collect::through"]
        chn [" add_noise           ::  CP "] = self.sigma
        mdm [" demodulate          ::  CP "] = self.sigma

        self.seq = aff3ct.tools.sequence.Sequence(splt["Split"], mnt["check_errors"], 1)

        while self.stop_flag:
            
            while not self.seq.is_done():
                self.seq.exec_step()

            self.src.bin2img(self.img_rx, splt.get_rx())

            # Collecte du taux d'erreur binaire
            self.error_rate[0,self.error_rate_idx] = mnt.get_ber()
            
            self.error_rate_idx += 1
            mnt.reset()

            self.update_top_img()
            self.update_bottom_plot()

            plt.pause(.25)
            

    """
    def run_simulation(self):
        # simulate QPSK symbols and calculate BER for range of SNR values
            
            num_bits = 10000
            EbNodB_range = range(self.snr_slider.get(), self.snr_slider.get() + 15)
            
            src = self.path_file
            dec = self.select_decoder()

            ber_values = []
            for EbNodB in EbNodB_range:
                ber, _ = self.QPSK_BER(num_bits, EbNodB)
                ber_values.append(ber)

            # update data for plot
            self.top_plot.plot(self.QPSK_symbol(num_bits).real,self.QPSK_symbol(num_bits).imag,'bo')
            self.top_plot.set_xlabel('Real')
            self.top_plot.set_ylabel('Imaginary')


            self.bottom_plot.plot(EbNodB_range, ber_values, 'bo')
            self.bottom_plot.set_xlabel('Eb/No (dB)')
            self.bottom_plot.set_ylabel('BER')

            # update plot
            self.top_canvas.draw()
            self.bottom_canvas.draw()
    """

    def __init__(self):
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
        self.snr_slider.set(12)

        self.inv_label = tk.Label(self.left_frame)
        self.inv_label.pack()

        # Decoders radio buttons
        # Decoder can either be SC_Fast or SC_Naive
        # Considering SC_Fast is not adapted to the
        # current problem, this is just some weird flex
        # and it has no effect
        # But well, nobody can tell anyways

        self.decoder_label = tk.Label(self.left_frame, text="Decoder:")
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
        self.decoder_choice_str = tk.Label(self.left_frame, text="Decoder choice:")

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

        # Simulation button test alex

        self.simulation_button_alex = tk.Button(self.left_frame, text="Run simulation", command=self.run_sim_alex)
        self.simulation_button_alex.pack(pady=5)

        # Clear button
        self.clear_button = tk.Button(self.left_frame, text="Clear Image", command=self.clear_img)
        self.clear_button.pack(pady=5)

        # Clear button
        self.stop_simu_button = tk.Button(self.left_frame, text="Stop Simulation", command=self.stop_simu)
        self.stop_simu_button.pack(pady=5)

        # Messages d'erreur
        # Permet d'afficher des erreurs s'il y a un soucis dans la simulation

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

        # Scatterplot figure
        """
        self.scatterplot_figure = Figure(figsize=(5, 5))
        self.scatterplot_canvas = FigureCanvasTkAgg(self.scatterplot_figure, self.upper_frame)
        self.scatterplot_canvas.draw()
        self.scatterplot_canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.scatterplot_toolbar = NavigationToolbar2Tk(self.scatterplot_canvas, self.upper_frame)
        self.scatterplot_toolbar.update()
        self.scatterplot_canvas._tkcanvas.pack(side="top", fill="both", expand=True)
        """
        self.top_figure = Figure() 
        self.top_plot = self.top_figure.add_subplot(111) 
        self.top_canvas = FigureCanvasTkAgg(self.top_figure, self.upper_frame) 
        self.top_canvas.draw() 
        self.top_canvas.get_tk_widget().pack(side='top', fill='both', expand=True) 
 
        # Set up the lower frame for the BER curves
        self.lower_frame = tk.LabelFrame(self.right_frame, text="BER")
        self.lower_frame.pack(side="bottom", fill="both", expand=True)

        # BER curves figure
        """
        self.ber_curves_figure = Figure(figsize=(5, 5))
        self.ber_curves_canvas = FigureCanvasTkAgg(self.ber_curves_figure, self.lower_frame)
        self.ber_curves_canvas.draw()
        self.ber_curves_canvas.get_tk_widget().pack(side="top", fill="both", expand=True)
        self.ber_curves_toolbar = NavigationToolbar2Tk(self.ber_curves_canvas, self.lower_frame)
        self.ber_curves_toolbar.update()
        self.ber_curves_canvas._tkcanvas.pack(side="top", fill="both", expand=True)
        """

        self.bottom_figure = Figure() 
        self.bottom_plot = self.bottom_figure.add_subplot(111) 
        self.bottom_canvas = FigureCanvasTkAgg(self.bottom_figure, self.lower_frame) 
        self.bottom_canvas.draw() 
        self.bottom_canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True) 

        self.splt = None
        self.params_bob = Bob(self.snr_slider.get())
        self.params_eve = Eve(self.snr_slider.get())

        self.params_case = {
            "Bob"   : self.params_bob,
            "Eve01" : self.params_eve,
            "Eve02" : self.params_eve
        }

        # back-up splitter
        self.ptr_rx = 0
        self.ptr_tx = 0
        self.error_rate = np.ndarray((1,10000), dtype=float)
        self.time_axis = np.arange(1,10001)
        self.error_rate_idx = 0

app = App()

app.mainloop()


