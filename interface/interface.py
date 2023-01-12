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


class App(tk.Tk):
    

    def open_file(self):
        # Open a file selection dialog
        self.path_file = fd.askopenfilename()

    def start(self):
        self.run_simulation()

    def stop(self):
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
            print(f"ValueError: No image selected.")
            return

        if(self.decoder.get() == ''):
            print(f"ValueError: No decoder selected.")
            return
    
        if(self.secrecy_mode.get() == ''):
            print(f"ValueError: No secrecy selected.")
            return

        K = 512      # taille a l'entree de l'encodeur
        sec_K = int(self.k_var.get())   # nombre de bits utiles
        N = int(self.n_var.get())     # taille a la sortie de l'encodeur
        ebn0 = self.snr_slider.get()    # SNR

        esn0 = ebn0 + 10*math.log10(K/N)
        sigma_val = 1/(math.sqrt(2)*10**(esn0/20))


        self.img =cv2.imread(self.path_file)[:,:,0] # image grayscale
        self.img_shape = self.img.shape
        
        self.img_rx = np.ndarray(shape=self.img_shape, dtype=np.uint8)

        # -- CHAINE DE COM

        # -- -- BITS GELES
        fbgen = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(K,N)
        noise = aff3ct.tools.noise.Sigma(sigma_val)
        fbgen.set_noise(noise)
        frozen_bits = fbgen.generate()

        # -- Source
        src = Source(self.img, K)

        # -- Splitter
        splt = Splitter(src.img_bin, len(src.img_bin), K)

        # -- encoder
        enc = aff3ct.module.encoder.Encoder_polar_sys(K, N, frozen_bits)

        # -- decoder
        dec = aff3ct.module.decoder.Decoder_polar_SC_naive_sys(K, N, frozen_bits)

        # -- modulator
        mdm = aff3ct.module.modem.Modem_BPSK_fast(N)

        # -- noise generator
        gen = aff3ct.tools.Gaussian_noise_generator_implem.FAST

        # -- channel
        chn = aff3ct.module.channel.Channel_AWGN_LLR(N, gen)

        # -- monitor
        mnt = aff3ct.module.monitor.Monitor_BFER_AR(K,1000,100)

        # -- Sigma sockets
        self.sigma = np.ndarray(shape = (1,1), dtype=np.float32)
        self.sigma[0,0] = sigma_val

        enc["encode::U_K"] = splt["Split::bit_seq"]
        mdm["modulate::X_N1"] = enc["encode::X_N"]
        chn["add_noise::X_N"] = mdm["modulate::X_N2"]
        mdm["demodulate::Y_N1"] = chn["add_noise::Y_N"]
        dec["decode_siho::Y_N"] = mdm["demodulate::Y_N2"]
        splt["Collect::buffer"] = dec["decode_siho::V_K"]
        mnt["check_errors::U"] = splt["Split::bit_seq"]
        mnt["check_errors::V"] = splt["Collect::through"]
        chn["add_noise::CP"] = self.sigma
        mdm["demodulate::CP"] = self.sigma

        self.seq = aff3ct.tools.sequence.Sequence(splt["Split"], mnt["check_errors"], 1)


        while self.stop_flag:
            print("Loop")
            while not self.seq.is_done():
                self.seq.exec_step()

            src.bin2img(self.img_rx, splt.get_rx())
            
            mnt.reset()

            self.update_top_img()
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
        self.title("Code Pol'eirb")
        self.geometry("1080x720")
        self.minsize(width=720, height=480)

        # Set up the left frame with the parameters
        self.left_frame = tk.LabelFrame(self, text="Paramètres")
        self.left_frame.pack(side="left", fill="both", expand=True)

        # SNR values slider
        self.snr_label = tk.Label(self.left_frame, text="SNR values:")
        self.snr_label.pack()
        self.snr_slider = tk.Scale(self.left_frame, from_=-4, to=30, orient="horizontal")
        self.snr_slider.pack()

        self.inv_label = tk.Label(self.left_frame)
        self.inv_label.pack()
        # Decoders radio buttons
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

        # K and N dropdown menus
        """
        self.k_label = tk.Label(self.left_frame, text="K:")
        self.k_label.grid(row=0, column=0, sticky="W", padx=10, pady=10)
        self.k_menu = tk.OptionMenu(self.left_frame, tk.StringVar(), *[8, 16, 32, 64, 128])
        self.k_menu.grid(row=0, column=1, sticky="W", padx=10, pady=10)
        self.n_label = tk.Label(self.left_frame, text="N:")
        self.n_label.grid(row=1, column=0, sticky="W", padx=10, pady=10)
        self.n_menu = tk.OptionMenu(self.left_frame, tk.StringVar(), *[1024, 2048, 4096, 8192, 16384])
        self.n_menu.grid(row=1, column=1, sticky="W", padx=10, pady=10)
        """

        self.inv_label2 = tk.Label(self.left_frame)
        self.inv_label2.pack()

        self.k_label = tk.Label(self.left_frame, text="Number of data bits K:")
        self.k_label.pack()
        self.k_var = tk.StringVar(self.left_frame) 
        self.k_var.set('64') 
        self.k_option = tk.OptionMenu(self.left_frame, self.k_var, *[8, 16, 32, 64, 128]) 
        self.k_option.pack() 

        self.inv_label3 = tk.Label(self.left_frame)
        self.inv_label3.pack()

        self.n_label = tk.Label(self.left_frame, text="Number of bits per packet N:")
        self.n_label.pack()
        self.n_var = tk.StringVar(self.left_frame) 
        self.n_var.set('1024') 
        self.n_option = tk.OptionMenu(self.left_frame, self.n_var, *[1024, 2048, 4096, 8192, 16384]) 
        self.n_option.pack() 
        
        self.inv_label4 = tk.Label(self.left_frame)
        self.inv_label4.pack()
        
        # Data rate dropdown menu
        self.data_rate_label = tk.Label(self.left_frame, text="Data rate (kb/s):")
        self.data_rate_label.pack()
        self.data_rate_var = tk.StringVar(self.left_frame) 
        self.data_rate_var.set('500') 
        self.data_rate_option = tk.OptionMenu(self.left_frame, self.data_rate_var, *[500, 1000, 5000]) 
        self.data_rate_option.pack()

        self.inv_label5 = tk.Label(self.left_frame)
        self.inv_label5.pack()

        # Secrecy mode radio buttons
        self.secrecy_mode_label = tk.Label(self.left_frame, text="Secrecy mode:")
        self.secrecy_mode_label.pack()
        self.secrecy_mode = tk.StringVar(self.left_frame)
        self.secrecy_mode.set('') 
        self.weak_button = tk.Radiobutton(self.left_frame, text='Weak', variable=self.secrecy_mode, value='weak') 
        self.weak_button.pack() 
        self.strong_button = tk.Radiobutton(self.left_frame, text='Strong', variable=self.secrecy_mode, value='strong') 
        self.strong_button.pack() 

        self.inv_label6 = tk.Label(self.left_frame)
        self.inv_label6.pack()

        # File input button
        self.file_button = tk.Button(self.left_frame, text="Select image", command=self.open_file)
        self.file_button.pack(pady=10)

        # Simulation button test alex
        self.simulation_button_alex = tk.Button(self.left_frame, text="Run simulation", command=self.run_sim_alex)
        self.simulation_button_alex.pack(pady=5)

        # Clear button
        self.clear_button = tk.Button(self.left_frame, text="Clear Image", command=self.clear_img)
        self.clear_button.pack(pady=5)

        # Clear button
        self.stop_simu_button = tk.Button(self.left_frame, text="Stop Simulation", command=self.stop_simu)
        self.stop_simu_button.pack(pady=5)

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



app = App()

app.mainloop()


