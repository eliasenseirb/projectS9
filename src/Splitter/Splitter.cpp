/*!
 * \file
 * \brief Separates a sequence of bits into frames.
 *
 * \section LICENSE
 * This file is under MIT license (https://openSplitter.org/licenses/MIT).
 */

#include "Module/Splitter/Splitter.hpp"

using namespace aff3ct;
using namespace aff3ct::module;

Splitter::
Splitter(const std::vector<int> & input, const size_t img_size, const size_t frame_len)
: Module(), input(input), img_size(img_size), frame_len(frame_len), tx_current_idx(0), rx_current_idx(0)
{
	const std::string name = "Splitter";
	this->set_name(name);
	this->set_short_name(name);
	this->tx_current_idx=0;
	this->rx_current_idx=0;
	// initialise le vecteur a 0
	std::fill_n(std::back_inserter(this->buffer), this->img_size, 0);

	// SPLIT TASK
	auto &p1 = this->create_task("Split");
	auto p1s_out = this->template create_socket_out<int32_t>(p1, "bit_seq", this->frame_len);
	this->create_codelet(p1, [p1s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Splitter&>(m)._splitter(static_cast<int32_t*>(t[p1s_out].get_dataptr()),
											frame_id);
		return 0;
	});

	// COLLECT TASK
	auto &p2 = this->create_task("Collect");
	auto p2s_in  = this->template create_socket_in<int32_t>(p2,"buffer",this->frame_len);
	auto p2s_out = this->template create_socket_out<int32_t>(p2,"through",this->frame_len);
	this->create_codelet(p2, [p2s_in, p2s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<Splitter&>(m)._collect(static_cast<int32_t*>(t[p2s_in].get_dataptr()),
										   static_cast<int32_t*>(t[p2s_out].get_dataptr()),
										   frame_id);
		return 0;
	});
}

void Splitter::
_splitter(int32_t * out, const size_t frame_id)
{
	for (size_t i = 0; i < this->frame_len; i++) {
		// write data in the socket
		out[i] = input[this->tx_current_idx++];
		if (this->tx_current_idx >= this->img_size) this->tx_current_idx = 0;
	}
}	

void Splitter::
_collect(int32_t * in, int32_t * through, const size_t frame_id)
{
	for (size_t i = 0; i < this->frame_len ; i++) {
		// read data from socket
		this->buffer[this->rx_current_idx++] = in[i];
		if (this->rx_current_idx >= this->img_size){ this->rx_current_idx = 0; std::cout<<"reset"<<std::endl;}
	}
	std::copy(in, in+this->frame_len, through);
}

std::vector<int32_t> Splitter::
get_rx()
{
	return this->buffer;
}

std::vector<int32_t> Splitter::
get_tx()
{
	return this->input;
}

size_t Splitter::
get_tx_ptr()
{
	return this->tx_current_idx;
}

size_t Splitter::
get_rx_ptr()
{
	return this->rx_current_idx;
}

size_t Splitter::
get_img_size()
{
	return this->img_size;
}

size_t Splitter::
get_frame_size()
{
	return this->frame_len;
}

void Splitter::
print_info()
{
	std::cout << "Buffer: " << &this->buffer << "\nInput: " << &this->input << std::endl;
}