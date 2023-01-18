"""

Fonctions pour gerer la recherche des bits geles et leur
position

"""

def all_no(bits_Bob: list[bool], bits_Eve: list[bool]):
	"""Fait une liste complete des bits sur lesquels ne pas envoyer"""
	out = [False for i in range(len(bits_Bob))]
	pos = []
	for i in range(len(bits_Bob)):
		out[i] = no(bits_Bob[i], bits_Eve[i])
		if out[i]:
			pos.append(i)
	return out, pos

def no(b1: bool, b2: bool):
	"""Trie les bits sur lesquels il ne faut pas envoyer"""
	return (not b1) and b2

def count(b: list[bool]):
	"""Compte les True dans une liste"""
	cnt = 0
	for bol in b:
		if bol:
			cnt+=1
	return cnt

def get_secrecy_position(frozen_bits, information_bits):
    """Trouve les positions dans la suite de K bits des
    bits de confidentialite.

    frozen_bits : list[bool] --> True si le bit est gele, False sinon
    information_bits: list[bool] --> Position des bits de confidentialite dans la liste de N bits
    """
    if information_bits == []:
        raise ValueError("No bits available for secrecy with this combination of EbN0 and penalty for Eve.")
    seq_ptr = 0
    info_idx = 0
    positions = []
    for i in range(len(frozen_bits)):
        if not frozen_bits[i]:
            # A chaque fois qu'on trouve un bit d'information
            # on avance dans la suite de K bits

            # Si cette position se trouve dans le tableau de bits
            # d'information, on la stocke
            # /!\ On travaille sous l'hypothese que les deux tableaux
            # sont tries
            
            print(f"{information_bits[info_idx]} vs {i}")
            if information_bits[info_idx] == i:
                positions.append(seq_ptr)
                info_idx += 1
            if info_idx == len(information_bits):
                return positions
            seq_ptr += 1

    return positions