/*!
 * \file
 * \brief Generates a message.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensplitter.org/licenses/MIT).
 */

#ifndef SPLITTER_HPP
#define SPLITTER_HPP

#include <vector>
#include <string>
#include <iostream>

#include "Module/Module.hpp"

namespace aff3ct
{
namespace module
{

/*!
 * \class Multiplexer
 *
 * \brief Compute the averaged power spectrum of the input signal.
 *
 */
class Splitter : public Module
{

protected:
	std::vector<int> input;  // image to send
	std::vector<int> buffer; // image received
    const size_t img_size;
    const size_t frame_len;
    size_t tx_current_idx;
	size_t rx_current_idx;

public:
	/*!
	 * \brief Constructor.
	 */
	Splitter(const std::vector<int> & input, const size_t img_size, const size_t frame_len);

	/*!
	 * \brief Destructor.
	 */
	virtual ~Splitter() = default;
	virtual std::vector<int32_t> get_rx();
	virtual std::vector<int32_t> get_tx();
	virtual size_t			     get_tx_ptr();
	virtual size_t			     get_rx_ptr();
	virtual size_t			     get_img_size();
	virtual size_t			     get_frame_size();
	

protected:
	virtual void _splitter  (int32_t * out, const size_t frame_id);
	virtual void _collect   (int32_t * in, int32_t * through, const size_t frame_id);
	
};
}
}

#endif /* SPLITTER_HPP */
