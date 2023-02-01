/*!
 * \file
 * \brief Separates a sequence of bits into frames.
 *
 * \section LICENSE
 * This file is under MIT license (https://openMutualInformation.org/licenses/MIT).
 */

#include "Module/MutualInformation/MutualInformation.hpp"

using namespace aff3ct;
using namespace aff3ct::module;

MutualInformation::
MutualInformation(const size_t frame_size)
: Module(), frame_size(frame_size), mui(0.0), limit_size(frame_size)
{
	const std::string name = "MutualInformation";
	this->set_name(name);
	this->set_short_name(name);

	// SPLIT TASK
	auto &p1 = this->create_task("compute");
	auto p1s_src = this->template create_socket_in <int32_t>(p1, "src", this->frame_size);
	auto p1s_rx = this->template create_socket_in <int32_t>(p1, "rx", this->frame_size);
	auto p1s_out = this->template create_socket_out<int32_t>(p1, "through", this->frame_size);
	this->create_codelet(p1, [p1s_src, p1s_rx, p1s_out](Module &m, Task &t, const size_t frame_id) -> int
	{
		static_cast<MutualInformation&>(m)._mutualinformation(static_cast<int32_t*>(t[p1s_src].get_dataptr()),
															  static_cast<int32_t*>(t[p1s_rx].get_dataptr()),
															  static_cast<int32_t*>(t[p1s_out].get_dataptr()),
															  frame_id);
		return 0;
	});
}

void MutualInformation::
_mutualinformation(const int32_t * src, const int32_t * rx, int32_t * through, const int frame_id)
{

	
	std::copy(rx, rx+this->frame_size, through);

	// proba jointe
	float pxy[2][2] = { {0.0, 0.0},
	                    {0.0, 0.0} };
	// proba marginales
	float px[2] = {0.0, 0.0};
	float py[2] = {0.0, 0.0};
	// info mutuelle
	float info = 0.0;

	// compte des 0, 1 dans les sequences recues
	for (size_t i = 0; i < this->limit_size; i++) 
	{
		pxy[src[i]][rx[i]]++; // ajout au compte
	}
	
	// estimation des probas
	for (size_t x = 0; x < 2; x++)
		for (size_t y = 0; y < 2; y++)
		{
			pxy[x][y]/=this->limit_size;
			// marginalisation
			px[x] += pxy[x][y];
			py[y] += pxy[x][y]; 
		}
	
	std::cout << "Probas estimées" << std::endl
		      << "+=====+=====+=====+" << std::endl
			  << "| X/Y |  0  |  1  |" << std::endl
			  << "+=====+=====+=====+" << std::endl
			  << "|  0  | " << std::fixed << std::setprecision(2) << pxy[0][0] << "| " << std::fixed << std::setprecision(2) << pxy[0][1] << std::endl
			  << "+=====+=====+=====+" << std::endl
			  << "|  1  | " << std::fixed << std::setprecision(2) << pxy[1][0] << "| " << std::fixed << std::setprecision(2) << pxy[1][1] << std::endl
			  << "+=====+=====+=====+" << std::endl;
	// calcul d'information mutuelle
	// voir rapport pour la formule
	for (size_t x = 0; x < 2; x++)
		for (size_t y = 0; y < 2; y++)
		{
			if (px[x] != 0 && py[y] != 0 && pxy[x][y] != 0)
				info += log2(pxy[x][y]/(px[x]*py[y])) * pxy[x][y];
		}
	std::cout << "Info mutuelle : " << info << std::endl;
	mui = info;
}

float MutualInformation::
get_mutual_information()
{
	return this->mui;
}

void MutualInformation::
set_limit(const size_t new_value)
{
	this->limit_size = new_value;
}