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
Multiplexer(const std::vector<int> & positions, const int N_code)
: Module(), positions(positions), N_code(N_code)
{
	const std::string name = "Multiplexer";
	this->set_name(name);
	this->set_short_name(name);

	auto &p1 = this->create_task("multiplexer");
	auto p1s_R = this->template create_socket_in <int32_t>(p1, "bad_bits", this->N_code);
	auto p1s_D = this->template create_socket_in <int32_t>(p1, "good_bits", this->positions.size());
	auto p1s_out = this->template create_socket_out<int32_t>(p1, "sig_mux_out", this->N_code);
	this->create_codelet(p1, [p1s_R, p1s_D, p1s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Multiplexer&>(m)._multiplexer(static_cast<int32_t*>(t[p1s_R].get_dataptr()),
		                                          static_cast<int32_t*>(t[p1s_D].get_dataptr()),
												  static_cast<int32_t*>(t[p1s_out].get_dataptr()),
										          frame_id);
		return 0;
	});
}

void Multiplexer::
_multiplexer(const int32_t * random_bits, const int32_t * data_bits, int32_t * out, const int frame_id)
{
	std::copy(random_bits, random_bits+this->N_code, out);
	for (size_t i = 0; i < this->positions.size(); i++)
		out[positions[i]] = data_bits[i];
}	

