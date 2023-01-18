#include "wrapper.hpp"
#include <pybind11/numpy.h>

namespace py = pybind11;
using namespace py::literals;
using namespace aff3ct;

// Create a	python module using PYBIND11, here our module will be named pyaf
PYBIND11_MODULE(pyaf, m){
	py::scoped_ostream_redirect stream_cout(
	std::cout,                                // std::ostream&
	py::module_::import("sys").attr("stdout") // Python output
	);
	py::scoped_ostream_redirect stream_cerr(
	std::cerr,                                // std::ostream&
	py::module_::import("sys").attr("stderr") // Python output
	);

	// Import AFF3CT module from py_AFF3CT
	py::object py_aff3ct_module = (py::object) py::module_::import("py_aff3ct").attr("module").attr("Module");
	
	py::module_ m_padder       = m.def_submodule("padder"      );
	py::class_<aff3ct::module::Padder>(m_padder,"Padder", py_aff3ct_module)
		.def(py::init<const int, const int>(), "init_size"_a, "final_size"_a);
	
	py::module_ m_multiplexer       = m.def_submodule("multiplexer"      );
	py::class_<aff3ct::module::Multiplexer>(m_multiplexer,"Multiplexer", py_aff3ct_module)
		.def(py::init<const std::vector<int> &, const int, const int>(), "positions"_a, "sec_sz"_a, "N_code"_a);
		
	py::module_ m_splitter = m.def_submodule("splitter");
	py::class_<aff3ct::module::Splitter>(m_splitter, "Splitter", py_aff3ct_module)
		.def(py::init<const std::vector<int> &, const size_t, const size_t>(), "input"_a, "img_size"_a, "frame_len"_a)
		.def("get_rx", [](aff3ct::module::Splitter& self){
			return self.get_rx();
		})
		.def("get_tx", [](aff3ct::module::Splitter& self){
			return self.get_tx();
		})
		.def("get_tx_ptr", [](aff3ct::module::Splitter& self){
			return self.get_tx_ptr();
		})
		.def("get_rx_ptr", [](aff3ct::module::Splitter& self){
			return self.get_rx_ptr();
		})
		.def("get_img_size", [](aff3ct::module::Splitter& self){
			return self.get_img_size();
		})
		.def("get_frame_size", [](aff3ct::module::Splitter& self){
			return self.get_frame_size();
		})
		.def("print_info", [](aff3ct::module::Splitter& self){
			self.print_info();
		})
		.def("set_rx_ptr", [](aff3ct::module::Splitter& self, const size_t new_value){
			self.set_rx_ptr(new_value);
		})
		.def("set_tx_ptr", [](aff3ct::module::Splitter& self, const size_t new_value){
			self.set_tx_ptr(new_value);
		});

	
	
	py::module_ m_filter       = m.def_submodule("filter"      );

	// Bind a custom class, here is the binding for the "aff3ct::module::Filter<float>" class.
	// py_aff3ct_module is here to indicate to pybind11 that aff3ct::module exists in py_AFF3CT
	py::class_<aff3ct::module::Filter<float>>(m_filter,"Filter", py_aff3ct_module);

	// Bind a custom class, here is the binding for the "aff3ct::module::Filter_FIR_ccr<float>" class.
	py::class_<aff3ct::module::Filter_FIR_ccr<float>, aff3ct::module::Filter<float>>(m_filter,"Filter_FIR_ccr")
		.def(py::init<const int, const std::vector<float>, const int>(), "N"_a, "h"_a, "n_frames"_a=1);

	// Bind a custom class, here is the binding for the "aff3ct::module::Filter_root_raised_cosine_ccr<float>" class.
	py::class_<aff3ct::module::Filter_root_raised_cosine_ccr<float>, aff3ct::module::Filter_FIR_ccr<float>>(m_filter,"Filter_root_raised_cosine_ccr")
		.def(py::init<const int,  const float, const int, const int, const int>(), "N"_a, "rolloff"_a = 0.05, "samples_per_symbol"_a = 4, "delay_in_symbol"_a = 50, "n_frames"_a=1)
		.def_static("synthetize", &aff3ct::module::Filter_root_raised_cosine_ccr<float>::synthetize);

	// Bind a custom class, here is the binding for the "aff3ct::module::Filter_UPFIR<float>" class.
	py::class_<aff3ct::module::Filter_UPFIR_ccr<float>, aff3ct::module::Filter<float>>(m_filter,"Filter_UPFIR_ccr")
		.def(py::init<const int, const std::vector<float>, const int, const int>(), "N"_a, "h"_a, "osf"_a = 1, "n_frames"_a=1);

	// Bind a custom class, here is the binding for the "aff3ct::module::Filter_Farrow_quad<float>" class.
	py::class_<aff3ct::module::Filter_Farrow_ccr<float>, aff3ct::module::Filter_FIR_ccr<float>>(m_filter,"Filter_Farrow_ccr")
		.def(py::init<const int, const float, const int>(), "N"_a, "mu"_a=0.0, "n_frames"_a=1);

	// Wrapping of Framer modules
	py::module_ m_framer       = m.def_submodule("framer"      );
	py::class_<aff3ct::module::Framer<float>>(m_framer,"Framer", py_aff3ct_module)
		.def(py::init<const int, const int, const std::string, const int>(), "xfec_frame_size"_a, "pl_frame_size"_a, "modcod"_a, "n_frames"_a=1);

	// Wrapping of Feedbacker modules
	py::module_ m_feedbacker   = m.def_submodule("feedbacker"  );
	py::class_<aff3ct::module::Feedbacker<float  >, std::unique_ptr<aff3ct::module::Feedbacker<float  >>>(m_feedbacker,"__Feedbacker_float",  py_aff3ct_module);
	py::class_<aff3ct::module::Feedbacker<int32_t>, std::unique_ptr<aff3ct::module::Feedbacker<int32_t>>>(m_feedbacker,"__Feedbacker_int32",  py_aff3ct_module);
	m_feedbacker.def("Feedbacker",[](const int N, const int32_t init_val)
	    {return std::unique_ptr<aff3ct::module::Feedbacker<int32_t>>(new aff3ct::module::Feedbacker<int32_t>(N,init_val));});
	m_feedbacker.def("Feedbacker",[](const int N, const float   init_val)
	    {return std::unique_ptr<aff3ct::module::Feedbacker<float  >>(new aff3ct::module::Feedbacker<float  >(N,init_val));});

	// Wrapping of Scrambler modules
	py::module_ m_scrambler    = m.def_submodule("scrambler"   );
	py::class_<aff3ct::module::Scrambler<int32_t>>(m_scrambler,"__Scrambler_int32", py_aff3ct_module);
	py::class_<aff3ct::module::Scrambler_BB<int32_t>,aff3ct::module::Scrambler<int32_t>>(m_scrambler,"Scrambler_BB")
		.def(py::init<const int, const int>(), "N"_a, "n_frames"_a=1);
	py::class_<aff3ct::module::Scrambler<float  >>(m_scrambler,"__Scrambler_float", py_aff3ct_module);
	py::class_<aff3ct::module::Scrambler_PL<float>,aff3ct::module::Scrambler<float>>(m_scrambler,"Scrambler_PL")
		.def(py::init<const int, const int, const int>(), "N"_a, "start_ix"_a, "n_frames"_a=1);

	// Wrapping of Estimator modules
	py::module_ m_estimator    = m.def_submodule("estimator"   );
	py::class_<aff3ct::module::Estimator<float>>(m_estimator,"__Estimator", py_aff3ct_module);
	py::class_<aff3ct::module::Estimator_DVBS2<float>, aff3ct::module::Estimator<float>>(m_estimator,"Estimator_DVBS2")
		.def(py::init<const int, const float, const int, const int>(), "N"_a, "code_rate"_a, "bps"_a, "n_frames"_a=1);

	py::module_ m_multiplier   = m.def_submodule("multiplier"  );
	py::class_<aff3ct::module::Multiplier<float>>(m_multiplier,"__Multiplier", py_aff3ct_module);
	py::class_<aff3ct::module::Multiplier_sine_ccc<float>, aff3ct::module::Multiplier<float>>(m_multiplier,"Multiplier_sine_ccc")
		.def(py::init<const int, const float, const float, const int>(), "N"_a, "f"_a, "Fs"_a=1.0f, "n_frames"_a=1);
	py::class_<aff3ct::module::Multiplier_sequence_ccc,aff3ct::module::Multiplier<float>>(m_multiplier,"Multiplier_sequence_ccc")
		.def(py::init<const int, const std::vector<float>&, const int>(), "N"_a, "sequence"_a, "n_frames"_a=1);
	py::class_<aff3ct::module::Multiplier_AGC_cc<float>,aff3ct::module::Multiplier<float>>(m_multiplier,"Multiplier_AGC_cc")
		.def(py::init<const int, const float, const int>(), "N"_a, "output_energy"_a=1.0f, "n_frames"_a=1);

	py::module_ m_synchronizer = m.def_submodule("synchronizer");
	py::module_ m_timing_synchronizer = m_synchronizer.def_submodule("timing");
	py::class_<aff3ct::module::Synchronizer_timing<>>(m_timing_synchronizer,"__Synchronizer_timing", py_aff3ct_module);
	py::class_<aff3ct::module::Synchronizer_Gardner_aib<>, aff3ct::module::Synchronizer_timing<>>(m_timing_synchronizer,"Synchronizer_Gardner")
		.def(py::init<const int, int, const float, const float, const float, const int>(), "N"_a, "osf"_a, "damping_factor"_a = std::sqrt(0.5), "normalized_bandwidth"_a = (float)5e-5, "detector_gain"_a = 2,  "n_frames"_a=1);
	py::class_<aff3ct::module::Synchronizer_Gardner_fast<>, aff3ct::module::Synchronizer_timing<>>(m_timing_synchronizer,"Synchronizer_Gardner_fast")
		.def(py::init<const int, int, const float, const float, const float, const int>(), "N"_a, "osf"_a, "damping_factor"_a = std::sqrt(0.5), "normalized_bandwidth"_a = (float)5e-5, "detector_gain"_a = 2,  "n_frames"_a=1);
	py::class_<aff3ct::module::Synchronizer_Gardner_fast_osf2<>, aff3ct::module::Synchronizer_timing<>>(m_timing_synchronizer,"Synchronizer_Gardner_fast_osf2")
		.def(py::init<const int, const float, const float, const float, const int>(), "N"_a, "damping_factor"_a = std::sqrt(0.5), "normalized_bandwidth"_a = (float)5e-5, "detector_gain"_a = 2,  "n_frames"_a=1);

	py::module_ m_freq_synchronizer = m_synchronizer.def_submodule("frequency");
	py::class_<aff3ct::module::Synchronizer_freq_coarse<float>>(m_freq_synchronizer,"__Synchronizer_freq_coarse", py_aff3ct_module);
	py::class_<aff3ct::module::Synchronizer_freq_coarse_DVBS2_aib<float>, aff3ct::module::Synchronizer_freq_coarse<float>>(m_freq_synchronizer,"Synchronizer_freq_coarse_DVBS2")
		.def(py::init<const int, const int, const float, const float, const int>(), "N"_a, "samples_per_symbol"_a = 4, "damping_factor"_a = std::sqrt(0.5), "normalized_bandwidth"_a = (float)1e-4,  "n_frames"_a=1);

	py::class_<aff3ct::module::Synchronizer_freq_fine<float>>(m_freq_synchronizer,"__Synchronizer_freq_fine", py_aff3ct_module);
	py::class_<aff3ct::module::Synchronizer_freq_phase_DVBS2_aib<float>, aff3ct::module::Synchronizer_freq_fine<float>>(m_freq_synchronizer,"Synchronizer_freq_phase_DVBS2")
		.def(py::init<const int, const int>(), "N"_a,  "n_frames"_a=1);
	py::class_<aff3ct::module::Synchronizer_Luise_Reggiannini_DVBS2_aib<float>, aff3ct::module::Synchronizer_freq_fine<float>>(m_freq_synchronizer,"Synchronizer_Luise_Reggiannini_DVBS2")
		.def(py::init<const int, const float, const int>(), "N"_a,  "alpha"_a, "n_frames"_a=1);

	py::module_ m_frame_synchronizer =  m_synchronizer.def_submodule("frame");
	py::class_<aff3ct::module::Synchronizer_frame<>>(m_frame_synchronizer,"__Synchronizer_frame", py_aff3ct_module);
	py::class_<aff3ct::module::Synchronizer_frame_DVBS2_aib<float>, aff3ct::module::Synchronizer_frame<float>>(m_frame_synchronizer,"Synchronizer_frame_DVBS2_aib")
		.def(py::init<const int, const float, const float, const int>(), "N"_a, "alpha"_a = 0.0f, "trigger"_a = 25.0f, "n_frames"_a=1);
	py::class_<aff3ct::module::Synchronizer_frame_DVBS2_fast<float>, aff3ct::module::Synchronizer_frame<float>>(m_frame_synchronizer,"Synchronizer_frame_DVBS2_fast")
		.def(py::init<const int, const float, const float, const int>(), "N"_a, "alpha"_a = 0.0f, "trigger"_a = 25.0f, "n_frames"_a=1);

	py::module_ m_decoder      = m.def_submodule("decoder"     );
	py::class_<aff3ct::module::Decoder_BCH_DVBS2<>,aff3ct::module::Decoder_BCH_std<>>(m_decoder,"Decoder_BCH_DVBS2")
		.def(py::init<const int&, const int&, const tools::BCH_polynomial_generator<int>&>(), "K"_a, "N"_a, "GF"_a);

	py::module_ m_encoder      = m.def_submodule("encoder"     );
	py::class_<aff3ct::module::Encoder_BCH_DVBS2<>,aff3ct::module::Encoder_BCH<>>(m_encoder,"Encoder_BCH_DVBS2")
		.def(py::init<const int&, const int&, const tools::BCH_polynomial_generator<int>&>(), "K"_a, "N"_a, "GF"_a);
	py::class_<aff3ct::module::Encoder_BCH_inter_DVBS2<>,aff3ct::module::Encoder_BCH_inter<>>(m_encoder,"Encoder_BCH_inter_DVBS2")
		.def(py::init<const int&, const int&, const tools::BCH_polynomial_generator<int>&>(), "K"_a, "N"_a, "GF"_a);



	py::module_ m_radio        = m.def_submodule("radio"       );
	#ifdef LINK_UHD
	py::class_<aff3ct::module::USRP_params>(m_radio,"USRP_params")
	.def(py::init<>())
	.def_readwrite("N",              &aff3ct::module::USRP_params::N             )
	.def_readwrite("threaded",       &aff3ct::module::USRP_params::threaded      )
	.def_readwrite("fifo_size",      &aff3ct::module::USRP_params::fifo_size     )
	.def_readwrite("type",           &aff3ct::module::USRP_params::type          )
	.def_readwrite("usrp_addr",      &aff3ct::module::USRP_params::usrp_addr     )
	.def_readwrite("clk_rate",       &aff3ct::module::USRP_params::clk_rate      )
	.def_readwrite("rx_enabled",     &aff3ct::module::USRP_params::rx_enabled    )
	.def_readwrite("rx_rate",        &aff3ct::module::USRP_params::rx_rate       )
	.def_readwrite("rx_subdev_spec", &aff3ct::module::USRP_params::rx_subdev_spec)
	.def_readwrite("rx_antenna",     &aff3ct::module::USRP_params::rx_antenna    )
	.def_readwrite("rx_freq",        &aff3ct::module::USRP_params::rx_freq       )
	.def_readwrite("rx_gain",        &aff3ct::module::USRP_params::rx_gain       )
	.def_readwrite("rx_filepath",    &aff3ct::module::USRP_params::rx_filepath   )
	.def_readwrite("tx_enabled",     &aff3ct::module::USRP_params::tx_enabled    )
	.def_readwrite("tx_rate",        &aff3ct::module::USRP_params::tx_rate       )
	.def_readwrite("tx_subdev_spec", &aff3ct::module::USRP_params::tx_subdev_spec)
	.def_readwrite("tx_antenna",     &aff3ct::module::USRP_params::tx_antenna    )
	.def_readwrite("tx_freq",        &aff3ct::module::USRP_params::tx_freq       )
	.def_readwrite("tx_gain",        &aff3ct::module::USRP_params::tx_gain       )
	.def_readwrite("tx_filepath",    &aff3ct::module::USRP_params::tx_filepath   );

	py::class_<aff3ct::module::Radio_USRP<float>, aff3ct::module::Module>(m_radio,"Radio_USRP")
		.def(py::init<const aff3ct::module::USRP_params&>(), "params"_a, "USRP parameter object.");

	#endif //LINK_UHD

	#ifdef LINK_FFTW
	py::module_ m_spectrum = m.def_submodule("spectrum");
	py::class_<aff3ct::module::Spectrum>(m_spectrum, "Spectrum", py_aff3ct_module)
		.def(py::init<const int, const int, const float, const float, const int>(), "N"_a, "W"_a, "alpha"_a = 0.0f, "Fs"_a = 1.0f, "Nfft"_a = 1024)
		.def("get_spectrum", [](aff3ct::module::Spectrum& self){
			py::array_t<float> spectrum(self.get_Nfft());
			py::buffer_info buf = spectrum.request();
			self.get_spectrum(static_cast<float *>(buf.ptr));
			return spectrum;
		})
		.def("get_freq", [](aff3ct::module::Spectrum& self){
			py::array_t<float> freq(self.get_Nfft());
			py::buffer_info buf = freq.request();
			self.get_freq(static_cast<float *>(buf.ptr));
			return freq;
		});
	#endif //LINK_FFTW
}