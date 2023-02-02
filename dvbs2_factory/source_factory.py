from py_aff3ct import module as mdl

class source_factory:
    """
    Factory for the source.
    Attributes
    ----------
    K : int
        Number of bits to generate
    type : str
        Type of source (default Random)
    file_path : str
        Path of the read file for "User" and "User_binary" sources. (default "")
    n_frames :
        Number of frames per task execution (default 1)
    """
    def __init__(self,
                 K,
                 type = "User_binary",
                 file_path = "./text.txt",
                 n_frames = 1):
        """
        Parameters
        ----------
        K : int
            Number of bits to generate
        type : str
            The type of source (default Random).
            Available Source types are :
             - "Random": Random binary source
             - "AZCW": All Zeros CodeWord
             - "User": Read the binary values from the file given in 'file_path'
             - "User_binary": Read in binary mode the file given in 'file_path'
        file_path : str
            Path of the read file for "User" and "User_binary" sources. (default "")
        n_frames :
            Number of frames per task execution (default 1)
        """
        self.K = K
        self.type = type
        self.file_path = file_path
        self.n_frames = n_frames

    def build(self):
        """
        Builds a source from the class attributes.
        """
        if self.type == "Random":
            source  = mdl.source.Source_random_fast(self.K)          
        elif self.type == "AZCW":
            source = mdl.source.Source_AZCW(self.K)
        elif self.type == "User":
            source = mdl.source.Source_user(self.K, self.file_path)
        elif self.type == "User_binary":
            source = mdl.source.Source_user_binary(self.K, self.file_path)
        source.n_frames = self.n_frames
        return source