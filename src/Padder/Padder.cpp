/*!
 * \file
 * \brief Computes the Padder of a complex signal.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */

#include "Module/Padder/Padder.hpp"

using namespace aff3ct;
using namespace aff3ct::module;

Padder::
Padder(const int init_size, const int final_size)
: Module(), init_size(init_size), final_size(final_size)
{
	const std::string name = "Padder";
	this->set_name(name);
	this->set_short_name(name);

	auto &p1 = this->create_task("padder");
	auto p1s_R = this->template create_socket_in <int32_t>(p1, "rand_bits", this->final_size);
	auto p1s_D = this->template create_socket_in <int32_t>(p1, "good_bits", this->init_size);
	auto p1s_out = this->template create_socket_out<int32_t>(p1, "sig_pad_out", this->final_size);
	this->create_codelet(p1, [p1s_R, p1s_D, p1s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Padder&>(m)._padder(static_cast<int32_t*>(t[p1s_R].get_dataptr()),
		                                          static_cast<int32_t*>(t[p1s_D].get_dataptr()),
												  static_cast<int32_t*>(t[p1s_out].get_dataptr()),
										          frame_id);
		return 0;
	});
	auto &p2 = this->create_task("unpadder");
	auto p2s_in = this->template create_socket_in <int32_t>(p2, "pad_sequence", this->final_size);
	auto p2s_out = this->template create_socket_out <int32_t>(p2, "good_bits", this->init_size);
	this->create_codelet(p2, [p2s_in, p2s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Padder&>(m)._unpadder(static_cast<int32_t*>(t[p2s_in].get_dataptr()),
													static_cast<int32_t*>(t[p2s_out].get_dataptr()),
													frame_id);
		return 0;
	});
	
}

void Padder::
_padder(const int32_t * random_bits, const int32_t * data_bits, int32_t * out, const int frame_id)
{
 
	std::copy(random_bits, random_bits+this->final_size, out);
    std::copy(data_bits, data_bits+this->init_size, out);
}	

void Padder::
_unpadder(const int32_t * pad_sequence, int32_t * good_bits, const int frame_id)
{
    
	std::copy(pad_sequence, pad_sequence+this->init_size, good_bits);
}