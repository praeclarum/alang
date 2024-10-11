from typing import TextIO, Union

class CodeWriter:
    def __init__(self, path_or_io: Union[str, TextIO]):
        if type(path_or_io) is str:
            self.out = open(path_or_io, "w")
            self.owner = True
        else:
            self.out = path_or_io
            self.owner = False
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    def write(self, s: str):
        self.out.write(s)
    def close(self):
        if self.owner and self.out is not None:
            self.out.close()
            self.out = None
            self.owner = False

    def write_function(self, f):
        raise NotImplementedError
    def write_struct(self, s):
        raise NotImplementedError
