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

	auto &p1 = this->create_task("pad");
	auto p1s_in = this->template create_socket_in <int32_t>(p1, "p_in", init_size);
	auto p1s_out = this->template create_socket_out<int32_t>(p1, "p_out", final_size);
	this->create_codelet(p1, [p1s_in, p1s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Padder&>(m)._pad(static_cast<int32_t*>(t[p1s_in].get_dataptr()),
									 static_cast<int32_t*>(t[p1s_out].get_dataptr()),
									 frame_id);
		return 0;
	});

	auto &p2 = this->create_task("pad2");
	auto p2s_in = this->template create_socket_in <int32_t>(p2, "p_in", init_size);
	auto p2s_r = this->template create_socket_in <int32_t>(p2, "r_in", final_size-init_size);
	auto p2s_out = this->template create_socket_out<int32_t>(p2, "p_out", final_size);
	this->create_codelet(p2, [p2s_in, p2s_r, p2s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Padder&>(m)._pad2(static_cast<int32_t*>(t[p2s_in].get_dataptr()),
									 static_cast<int32_t*>(t[p2s_r] .get_dataptr()),
									 static_cast<int32_t*>(t[p2s_out].get_dataptr()),
									 frame_id);
		return 0;
	});	
	
}

void Padder::
_pad(const int32_t* sig_in, int32_t* sig_out, const int frame_id)
{
	for (int i = 0; i < this->final_size; i+=2)
	{
		sig_out[i] = 0;
		sig_out[i+1] = 1;
	}
	std::copy(sig_in, sig_in+this->init_size, sig_out);
}	

void Padder::
_pad2(const int32_t* sig_in, const int32_t* r_in, int32_t* sig_out, const int frame_id)
{
	std::copy(r_in, r_in+this->final_size-this->init_size, sig_out+this->init_size);
	std::copy(sig_in, sig_in+this->init_size, sig_out);
}	
