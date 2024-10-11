from typing import TextIO, Union
from langs.language import Language, register_language
from langs.writer import CodeWriter

class AWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO]):
        super().__init__(out)

class ALanguage(Language):
    def __init__(self):
        super().__init__("a")

    def open_writer(self, out: Union[str, TextIO]) -> AWriter:
        return AWriter(out)

a_lang = ALanguage()
register_language(a_lang)
