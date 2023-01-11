/*!
 * \file
 * \brief Computes the Multiplexer of a complex signal.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */

#include "Module/Multiplexer/Multiplexer.hpp"

using namespace aff3ct;
using namespace aff3ct::module;

Multiplexer::
Multiplexer(const std::vector<int> & positions, const int sec_sz, const int N_code)
: Module(), positions(positions), sec_sz(sec_sz), N_code(N_code)
{
	const std::string name = "Multiplexer";
	this->set_name(name);
	this->set_short_name(name);

	auto &p1 = this->create_task("multiplexer");
	auto p1s_R = this->template create_socket_in <int32_t>(p1, "bad_bits", this->N_code);
	auto p1s_D = this->template create_socket_in <int32_t>(p1, "good_bits", this->sec_sz);
	auto p1s_out = this->template create_socket_out<int32_t>(p1, "sig_mux_out", this->N_code);
	this->create_codelet(p1, [p1s_R, p1s_D, p1s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Multiplexer&>(m)._multiplexer(static_cast<int32_t*>(t[p1s_R].get_dataptr()),
		                                          static_cast<int32_t*>(t[p1s_D].get_dataptr()),
												  static_cast<int32_t*>(t[p1s_out].get_dataptr()),
										          frame_id);
		return 0;
	});
	auto &p2 = this->create_task("demultiplexer");
	auto p2s_in = this->template create_socket_in <int32_t>(p2, "mux_sequence", this->N_code);
	auto p2s_out = this->template create_socket_out <int32_t>(p2, "good_bits", this->sec_sz);
	this->create_codelet(p2, [p2s_in, p2s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Multiplexer&>(m)._demultiplexer(static_cast<int32_t*>(t[p2s_in].get_dataptr()),
													static_cast<int32_t*>(t[p2s_out].get_dataptr()),
													frame_id);
		return 0;
	});
	
}

void Multiplexer::
_multiplexer(const int32_t * random_bits, const int32_t * data_bits, int32_t * out, const int frame_id)
{
	
	for (size_t i = 0; i < this->positions.size(); i++)
		out[this->positions[i]] = data_bits[i];
}	

void Multiplexer::
_demultiplexer(const int32_t * mux_sequence, int32_t * good_bits, const int frame_id)
{
	
	for (size_t i = 0; i < this->positions.size(); i++) {	
		//std::cout << i << " Position " << this->positions[i] << std::endl;	
		good_bits[i] = mux_sequence[this->positions[i]];
	}
}
