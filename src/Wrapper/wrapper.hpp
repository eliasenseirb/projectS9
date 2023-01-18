#ifndef WRAPPER_HPP_
#define WRAPPER_HPP_
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/iostream.h>

#include <vector>

#include "Module/Filter/Filter.hpp"
#include "Module/Filter/Filter_FIR/Filter_FIR_ccr.hpp"
#include "Module/Filter/Filter_FIR/Filter_RRC/Filter_root_raised_cosine_ccr.hpp"
#include "Module/Filter/Filter_FIR/Farrow/Filter_Farrow_ccr.hpp"

#include "Module/Filter/Filter_UPFIR/Filter_UPFIR_ccr.hpp"

#include "Module/Framer/Framer.hpp"
#include "Module/Multiplexer/Multiplexer.hpp"
#include "Module/Splitter/Splitter.hpp"
#include "Module/Padder/Padder.hpp"
#include "Module/Feedbacker/Feedbacker.hpp"

#include "Module/Scrambler/Scrambler.hpp"
#include "Module/Scrambler/Scrambler_BB/Scrambler_BB.hpp"
#include "Module/Scrambler/Scrambler_PL/Scrambler_PL.hpp"

#include "Module/Estimator/Estimator.hpp"
#include "Module/Estimator/Estimator_DVBS2.hpp"

#include "Module/Decoder_BCH_DVBS2/Decoder_BCH_DVBS2.hpp"
#include "Module/Encoder_BCH_DVBS2/Encoder_BCH_DVBS2.hpp"
#include "Module/Encoder_BCH_DVBS2/Encoder_BCH_inter_DVBS2.hpp"

#include "Module/Multiplier/Multiplier.hpp"
#include "Module/Multiplier/Sequence/Multiplier_sequence_ccc.hpp"
#include "Module/Multiplier/Sequence/Multiplier_AGC_cc.hpp"
#include "Module/Multiplier/Sine/Multiplier_sine_ccc.hpp"

#include "Module/Synchronizer/Synchronizer_timing/Synchronizer_timing.hpp"
#include "Module/Synchronizer/Synchronizer_timing/Synchronizer_Gardner_aib.hpp"
#include "Module/Synchronizer/Synchronizer_timing/Synchronizer_Gardner_fast.hpp"
#include "Module/Synchronizer/Synchronizer_timing/Synchronizer_Gardner_fast_osf2.hpp"

#include "Module/Synchronizer/Synchronizer_freq/Synchronizer_freq_coarse/Synchronizer_freq_coarse.hpp"
#include "Module/Synchronizer/Synchronizer_freq/Synchronizer_freq_coarse/Synchronizer_freq_coarse_DVBS2_aib.hpp"
#include "Module/Synchronizer/Synchronizer_freq/Synchronizer_freq_fine/Synchronizer_freq_fine.hpp"
#include "Module/Synchronizer/Synchronizer_freq/Synchronizer_freq_fine/Synchronizer_freq_phase_DVBS2_aib.hpp"
#include "Module/Synchronizer/Synchronizer_freq/Synchronizer_freq_fine/Synchronizer_Luise_Reggiannini_DVBS2_aib.hpp"

#include "Module/Synchronizer/Synchronizer_frame/Synchronizer_frame.hpp"
#include "Module/Synchronizer/Synchronizer_frame/Synchronizer_frame_DVBS2_aib.hpp"
#include "Module/Synchronizer/Synchronizer_frame/Synchronizer_frame_DVBS2_fast.hpp"

#include "Module/Radio/Radio.hpp"

#ifdef LINK_UHD
#include "Module/Radio/Radio_USRP/Radio_USRP.hpp"
#endif //LINK_UHD

#ifdef LINK_FFTW
#include "Module/Spectrum/Spectrum.hpp"
#endif //LINK_FFTW
#endif /* WRAPPER_HPP_ */
