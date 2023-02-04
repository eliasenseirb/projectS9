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
#import threading

load_dotenv()
# ensure we can find aff3ct
sys.path.append(os.getenv("AFF3CT_PATH"))
sys.path.append(os.getenv("PYAF_PATH"))

sys.path.append("../src")
sys.path.append("./src")

import py_aff3ct as aff3ct
import py_aff3ct.module.encoder as af_enc
import pyaf
from pyaf.splitter import Splitter
from pyaf.multiplexer import Multiplexer
from source_nomod import Source
from frozenbits_handler import all_no, no, get_secrecy_position, count
from params import Bob, Eve
from sim import Sim

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

    def format_img(self, img: list[int], img_shape: tuple[int, int]) -> np.ndarray :
        """Transform an int list into np.uint8"""
        if len(img) != 8*img_shape[0]*img_shape[1]:
            raise ValueError(f"Error ! Array size {len(img)} does not match the image format ({img_shape[0]}, {img_shape[1]})")

        img_uint8 = [np.uint8(x) for x in img]
        img_reshaped = np.reshape(img_uint8, img_shape)

        return img_reshaped
    
    def update_top_img(self):
        """Update the top plot"""
        self.top_plot.imshow(self.img_rx, cmap='gist_gray')
        self.top_plot.set_xlabel('pixels')
        self.top_plot.set_ylabel('pixels')
        self.top_plot.axis('off')
        self.top_canvas.draw()
        self.top_canvas.flush_events()

    def update_bottom_plot(self):
        """Update the bottom plot"""
        if self.mutual_information_idx > 10:
            left  = self.mutual_information_idx-10
            right = self.mutual_information_idx
        else:
            left  = 0 
            right = 10

        self.bottom_plot.cla()
        slg = self.bottom_plot.plot(self.time_axis, self.mutual_information[0,:])
        self.bottom_plot.set_xlim(left, right)
        self.bottom_plot.set_ylim(-0.1, 1.1)
        self.bottom_plot.set_title("Mutual Information")
        self.bottom_plot.set_xlabel("Time")
        self.bottom_plot.set_ylabel("I(X;Y)")
        self.bottom_plot.grid()
        self.bottom_canvas.draw()

    def clear_img(self):
        """Clear the image plot"""
        img_vide = np.zeros((2,2), dtype=int)
        self.top_plot.imshow(img_vide, cmap='gist_gray')
        self.top_plot.set_xlabel('')
        self.top_plot.set_ylabel('')
        self.top_canvas.draw()
    
    def stop_simu(self):
        """Stop receiving"""
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
            # use other decoder, to be defined
            dec = aff3ct.module.decoder.Decoder_other(K, N, frozen_bits)
        return dec

    def run_sim(self):
        self._run_sim()

    def _run_sim(self):
        """Error check then run the simulation"""
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

        if (self.secrecy_mode.get() == 'strong'):
            self.error_msg.set("Strong secrecy is not implemented yet.")
            return

        self.params_bob = Bob(self.snr_slider.get())
        self.params_eve = Eve(self.snr_slider.get())

        dec_choice = self.decoder_choice.get()

        sim = Sim(self.src.img_bin, ebn0=self.snr_slider.get(), decoder=dec_choice, Eve_has_mux=self.Eve_has_mux.get(), secrecy=self.secrecy_mode.get())

        self.seq = sim.sequence 

        while self.stop_flag:
            
            while not self.seq.is_done():
                self.seq.exec_step()
                
            self.src.bin2img(self.img_rx, sim.rx)

            # collecting BER and mutual information
            self.ber, self.mutual_information[0,self.mutual_information_idx] = sim.stats
            sec_sz = sim.N
            self.ber_msg.set(f"Last frame BER: {self.ber:.2f}")
            self.N_msg.set(f"Information bits: {sec_sz}")
            
            self.mutual_information_idx += 1

            self.update_top_img()
            self.update_bottom_plot()

            plt.pause(.25)
            
    def __init__(self):
        """Constructor.
        Setup the different buttons for the GUI
        """
        tk.Tk.__init__(self)

        self.path_file = ""
        self.title("Pol'eirb Codes")
        self.geometry("1080x720")
        self.minsize(width=720, height=980)

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
        self.snr_slider.set(7)

        self.inv_label = tk.Label(self.left_frame)
        self.inv_label.pack()

        # Decoders radio buttons
        # Decoder can either be SC_Fast or SC_Naive

        self.decoder_label = tk.Label(self.left_frame, text="Decoder:")
        self.decoder_label.pack()
        self.decoder = tk.StringVar(self.left_frame)
        self.decoder.set('') 
        self.sc_fast_button = tk.Radiobutton(self.left_frame, text='SC Fast', variable=self.decoder, value='sc_fast') 
        self.sc_fast_button.configure(state=tk.DISABLED)
        self.sc_naive_button = tk.Radiobutton(self.left_frame, text='SC Naive', variable=self.decoder, value='sc_naive') 
        self.sc_naive_button.pack() 
        self.other_button = tk.Radiobutton(self.left_frame, text='Other', variable=self.decoder, value='other') 
        self.sc_fast_button.pack() 
        self.other_button.pack()
        self.other_button.configure(state=tk.DISABLED)
        self.sc_naive_button.select()

        self.inv_label5 = tk.Label(self.left_frame)
        self.inv_label5.pack()

        # Secrecy mode radio buttons
        # Allow to choose between weak secrecy and strong secrecy
        # this one is for future use, since strong secrecy is not
        # implemented.

        self.secrecy_mode_label = tk.Label(self.left_frame, text="Secrecy mode:")
        self.secrecy_mode = tk.StringVar(self.left_frame)
        self.secrecy_mode.set('') 
        self.none_button   = tk.Radiobutton(self.left_frame, text='None', variable=self.secrecy_mode, value='none')
        self.weak_button   = tk.Radiobutton(self.left_frame, text='Weak', variable=self.secrecy_mode, value='weak') 
        self.strong_button = tk.Radiobutton(self.left_frame, text='Strong', variable=self.secrecy_mode, value='strong') 

        self.secrecy_mode_label.pack()
        self.weak_button.pack() 
        self.strong_button.pack() 
        self.strong_button.configure(state=tk.DISABLED)
        self.weak_button.select()
        self.none_button.pack()
        self.none_button.configure(state=tk.DISABLED)

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
        self.decoder_choice_eve01 = tk.Radiobutton(self.left_frame, text="Eve", variable = self.decoder_choice, value = "Eve")
        
        self.decoder_choice_str.pack()
        self.decoder_choice_bob.pack()
        self.decoder_choice_eve01.pack()

        self.decoder_choice_bob.select()

        self.inv_label7 = tk.Label(self.left_frame)
        self.inv_label7.pack()

        # Mux choice button
        # Allows to choose if Eve has the demultiplexer
        # or not. No effect for Bob, he will always have
        # it.

        self.Eve_has_mux = tk.BooleanVar()
        self.mux_choice_str = tk.Label(self.left_frame, text="Mux choice (Eve only):")

        self.mux_choice_on  = tk.Radiobutton(self.left_frame, text="On", variable=self.Eve_has_mux, value=True)
        self.mux_choice_off = tk.Radiobutton(self.left_frame, text="Off", variable=self.Eve_has_mux, value=False)

       
        self.mux_choice_str.pack()
        self.mux_choice_off.pack()
        self.mux_choice_on.pack() 

        self.mux_choice_off.select()

        self.inv_label8 = tk.Label(self.left_frame)
        self.inv_label8.pack()

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

        self.simulation_button = tk.Button(self.left_frame, text="Run simulation", command=self.run_sim)
        self.simulation_button.pack(pady=5)

        # Clear button
        self.clear_button = tk.Button(self.left_frame, text="Clear Image", command=self.clear_img)
        self.clear_button.pack(pady=5)

        # Clear button
        self.stop_simu_button = tk.Button(self.left_frame, text="Stop Simulation", command=self.stop_simu)
        self.stop_simu_button.pack(pady=5)

        # Error messages
        # Allows for error messages display during the simulation
        self.inv_label9 = tk.Label(self.left_frame)
        self.inv_label9.pack()

        self.ber_msg      = tk.StringVar()
        self.N_msg        = tk.StringVar()
        self.error_msg    = tk.StringVar()

        self.ber_msg.set   ("Last frame BER: ")
        self.N_msg.set     ("Information bits: ")
        self.error_msg.set ("")

        self.ber_output   = tk.Label(self.left_frame, textvariable=self.ber_msg)
        self.N_output     = tk.Label(self.left_frame, textvariable=self.N_msg)
        self.error_output = tk.Label(self.left_frame, textvariable=self.error_msg, fg='#ff0000')

        self.ber_output.pack()
        self.N_output.pack()
        self.error_output.pack()

        # Set up the right frame with the plots
        self.right_frame = tk.LabelFrame(self, text="Figures")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Set up the upper frame for the image
        self.upper_frame = tk.LabelFrame(self.right_frame, text="Image received")
        self.upper_frame.pack(side="top", fill="both", expand=True)

        # Top figure
        
        self.top_figure = Figure() 
        self.top_plot = self.top_figure.add_subplot(111) 
        self.top_canvas = FigureCanvasTkAgg(self.top_figure, self.upper_frame) 
        self.top_canvas.draw() 
        self.top_canvas.get_tk_widget().pack(side='top', fill='both', expand=True) 
 
        # Set up the lower frame for the BER curves
        self.lower_frame = tk.LabelFrame(self.right_frame, text="Mutual information")
        self.lower_frame.pack(side="bottom", fill="both", expand=True)

        # BER curves figure

        self.bottom_figure = Figure() 
        self.bottom_plot = self.bottom_figure.add_subplot(111) 
        self.bottom_canvas = FigureCanvasTkAgg(self.bottom_figure, self.lower_frame) 
        self.bottom_canvas.draw() 
        self.bottom_canvas.get_tk_widget().pack(side='bottom', fill='both', expand=True) 

        self.splt = None
        self.params_bob = Bob(self.snr_slider.get())
        self.params_eve = Eve(self.snr_slider.get())

        # pseudo-switch case statement for Python
        # For compatibility with versions 3.7, 3.8 and 3.9
        self.params_case = {
            "Bob": self.params_bob,
            "Eve": self.params_eve,   
        }

        self.ptr_rx = 0
        self.ptr_tx = 0
        self.ber = 0
        self.mutual_information = np.ndarray((1,10000), dtype=float)
        self.time_axis = np.arange(1,10001)
        self.mutual_information_idx = 0
        self.threads = list()

app = App()
app.bind('<Escape>', lambda e: close_win(e))

def close_win(e):
    app.destroy()

app.mainloop()


