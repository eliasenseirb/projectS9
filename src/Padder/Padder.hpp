/*!
 * \file
 * \brief Generates a message.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */

#ifndef PADDER_HPP
#define PADDER_HPP

#include <vector>
#include <string>
#include <iostream>

#include "Module/Module.hpp"

namespace aff3ct
{
namespace module
{

/*!
 * \class Padder
 *
 * \brief Compute the averaged power spectrum of the input signal.
 *
 */
class Padder : public Module
{

protected:
	int init_size;
	int final_size;



public:
	/*!
	 * \brief Constructor.
	 */
	Padder(const int init_size, const int final_size);

	/*!
	 * \brief Destructor.
	 */
	virtual ~Padder() = default;

protected:

	virtual void _padder  (const int32_t * random_bits, const int32_t * data_bits, int32_t* out, const int frame_id);
  virtual void _unpadder (const int32_t * pad_sequence, int32_t * good_bits, const int frame_id);


};
}
}

#endif /* PADDER_HPP */
