from typing import TextIO, Union
from langs.language import Language, register_language
from langs.writer import CodeWriter

class CWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO]):
        super().__init__(out)

class CLanguage(Language):
    def __init__(self):
        super().__init__("c")

    def open_writer(self, out: Union[str, TextIO]) -> CWriter:
        return CWriter(out)

c_lang = CLanguage()
register_language(c_lang)

