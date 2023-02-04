import py_aff3ct as aff3ct
"""

Functions handling frozen bits position

"""

def all_no(bits_Bob, bits_Eve):
	"""
    List all the bits which are effective for Bob and
    ineffective for Eve
    """
	out = [False for i in range(len(bits_Bob))]
	pos = []
	for i in range(len(bits_Bob)):
		out[i] = no(bits_Bob[i], bits_Eve[i])
		if out[i]:
			pos.append(i)
	return out, pos

def no(b1: bool, b2: bool):
	"""Return `False` if the bit isn't secretive"""
	return (not b1) and b2

def count(b):
	"""Counts how many `True` are in a list"""
	cnt = 0
	for bol in b:
		if bol:
			cnt+=1
	return cnt

def get_secrecy_position(frozen_bits, information_bits):
    """Find the position of every `True` in a list

    Returns:
    frozen_bits : list[bool] --> `True` if the bit is frozen, `False` else
    information_bits: list[bool] --> Every secrecy bits' positions as a list
    """
    if information_bits == []:
        raise ValueError("No bits available for secrecy with this combination of EbN0 and penalty for Eve.")
    seq_ptr = 0
    info_idx = 0
    positions = []
    for i in range(len(frozen_bits)):
        if not frozen_bits[i]:
            # Every time an information bit is found
            # we go one step further in the K bits sequence

            # If this position is bound to an information bit
            # it gets saved
            # Note that this function works under the hypothesis that
            # both lists are sorted
            
            if information_bits[info_idx] == i:
                positions.append(seq_ptr)
                info_idx += 1
        
            if info_idx == len(information_bits):
                return positions
            seq_ptr += 1

    return positions

def gen_frozen(Bob, Eve):
    """Generate frozen bits for Bob and Eve"""
    # Bob's frozen bits
    fbgen_bob = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(Bob.frozen_K,Bob.N)
    Bob.noise = aff3ct.tools.noise.Sigma(Bob.sigma)
    fbgen_bob.set_noise(Bob.noise)
    Bob.frozen_bits = fbgen_bob.generate()

    # Eve's frozen bits
    fbgen_eve = aff3ct.tools.frozenbits_generator.Frozenbits_generator_GA_Arikan(Eve.frozen_K,Eve.N)
    Eve.noise = aff3ct.tools.noise.Sigma(Eve.sigma)
    fbgen_eve.set_noise(Eve.noise)
    Eve.frozen_bits = fbgen_eve.generate()

def weak_secrecy(Bob, Eve):
    """
    Generate the frozen bits for Bob and Eve
    Then return every secrecy bit's position and their amount
    """
    gen_frozen(Bob, Eve)

    mux_bits, pos_mux_bits = all_no(Bob.frozen_bits, Eve.frozen_bits)

    sec_sz = count(mux_bits)

    return get_secrecy_position(Bob.frozen_bits, pos_mux_bits), sec_sz
