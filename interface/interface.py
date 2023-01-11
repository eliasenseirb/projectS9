import tkinter as tk
import tkinter.filedialog as fd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import numpy as np 

class App(tk.Tk):

    def open_file(self):
        # Open a file selection dialog
        self.path_file = fd.askopenfilename()

    def start(self):
        self.run_simulation()

    def stop(self):
        self.left_frame.after_cancel(self._job)
    
    def QPSK_symbol(self, num_bits):
        # generate random bits
        self.source = np.random.randint(2, size=num_bits)

        # map bits to QPSK symbols
        symbols = np.empty(len(self.source) // 2, dtype=complex)
        symbols.real = self.source[::2]/np.sqrt(2)
        symbols.imag = self.source[1::2]/np.sqrt(2)

        return symbols

    def QPSK_demod(self, symbols, noise_variance):
        # demodulate QPSK symbols
        decision = symbols.real > 0
        decision = decision.astype(float)  # convert decision to float

        # add noise to decision
        decision += np.random.normal(scale=np.sqrt(noise_variance), size=decision.shape)

        # map decisions to bits
        bits = np.empty(len(symbols) * 2, dtype=int)
        bits[::2] = decision > 0
        bits[1::2] = decision < 0

        return bits

    def QPSK_BER(self, num_bits, EbNodB):
        # generate QPSK symbols
        symbols = self.QPSK_symbol(num_bits)

        # calculate noise variance
        noise_variance = 1 / (10 ** (EbNodB / 10.0))

        # demodulate QPSK symbols
        bits = self.QPSK_demod(symbols, noise_variance)

        # calculate BER and SER
        n_errors = np.sum(bits != self.source)
        ber = float(n_errors) / float(num_bits)
        ser = float(n_errors) / float(len(symbols))

        return ber, ser
    
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


    def select_decoder(self):
        K = self.k_var.get()  # replace with desired value
        N = self.n_var.get()  # replace with desired value
        frozen_bits = np.zeros(int(K), dtype=int)  # replace with desired value

        #retirer les "" pour affilier la bonne valeur au décodeur
        decoder = self.decoder.get()
        if decoder == 'sc_fast':
            dec = "aff3ct.module.decoder.Decoder_polar_SC_fast_sys(K, N, frozen_bits)"
        elif decoder == 'sc_naive':
            dec = "aff3ct.module.decoder.Decoder_polar_SC_naive_sys(K, N, frozen_bits)"
        else:
            # use other decoder
            dec = "aff3ct.module.decoder.Decoder_other(K, N, frozen_bits)"
        return dec


    def __init__(self):
        tk.Tk.__init__(self)

        self.path_file = ""
        self.title("Code Pol'eirb")
        self.geometry("1440x1080")
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
        self.k_var.set('8') 
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
        self.weak_button = tk.Radiobutton(self.left_frame, text='Weak', variable=self.secrecy_mode, value='weak') 
        self.weak_button.pack() 
        self.strong_button = tk.Radiobutton(self.left_frame, text='Strong', variable=self.secrecy_mode, value='strong') 
        self.strong_button.pack() 

        self.inv_label6 = tk.Label(self.left_frame)
        self.inv_label6.pack()

        # File input button
        self.file_button = tk.Button(self.left_frame, text="Select image", command=self.open_file)
        self.file_button.pack(pady=20)

        # Simulation button
        self.simulation_button = tk.Button(self.left_frame, text="Run simulation", command=self.run_simulation)
        self.simulation_button.pack(pady=10)

        # Set up the right frame with the plots
        self.right_frame = tk.LabelFrame(self, text="Figures")
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Set up the upper frame for the scatterplot
        self.upper_frame = tk.LabelFrame(self.right_frame, text="Scatterplot")
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




