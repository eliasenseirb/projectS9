/*!
 * \file
 * \brief Generates a message.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */

#ifndef MULTIPLEXER_HPP
#define MULTIPLEXER_HPP

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
class Multiplexer : public Module
{

protected:
	std::vector<int> positions;
	int N_code;


public:
	/*!
	 * \brief Constructor.
	 */
	Multiplexer(const std::vector<int> & positions, const int N_code);

	/*!
	 * \brief Destructor.
	 */
	virtual ~Multiplexer() = default;

protected:
	virtual void _multiplexer  (const int32_t * random_bits, const int32_t * data_bits, int32_t* out, const int frame_id);
};
}
}

#endif /* MULTIPLEXER_HPP */
