/*!
 * \file
 * \brief Generates a message.
 *
 * \section LICENSE
 * This file is under MIT license (https://opensource.org/licenses/MIT).
 */

#ifndef MUTUALINFORMATION_HPP
#define MUTUALINFORMATION_HPP

#include <vector>
#include <string>
#include <iostream>
#include <math.h>

#include "Module/Module.hpp"

namespace aff3ct
{
namespace module
{

/*!
 * \class MutualInformation
 *
 * \brief Compute the averaged power spectrum of the input signal.
 *
 */
class MutualInformation : public Module
{

protected:
	const size_t frame_size;
	float mui;
	size_t limit_size;

public:
	/*!
	 * \brief Constructor.
	 */
	MutualInformation(const size_t frame_size);
	

	/*!
	 * \brief Destructor.
	 */
	virtual ~MutualInformation() = default;

	/*!
	 * \brief Getter.
	 */
	virtual float get_mutual_information ();
	virtual void  set_limit              (const size_t new_value);

protected:
	virtual void _mutualinformation  (const int32_t * src, const int32_t * rx, int32_t * through, const int frame_id);
	
};

}
}
#endif /* MUTUALINFORMATION_HPP */
