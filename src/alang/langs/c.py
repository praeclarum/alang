from typing import Optional, TextIO, Union
from langs.language import Language, register_language
from langs.writer import CodeWriter

class CWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

class CLanguage(Language):
    def __init__(self):
        super().__init__("c")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> CWriter: # type: ignore
        return CWriter(out, options)

c_lang = CLanguage()
register_language(c_lang)

