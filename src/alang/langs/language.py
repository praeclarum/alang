from typing import Any, Optional, TextIO, Union
from langs.writer import CodeWriter

class Language:
    def __init__(self, name: str):
        self.name = name
    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> CodeWriter: # type: ignore
        return CodeWriter(out, options)
    def parse_expr(self, code: str):
        raise NotImplementedError()

language_registry = {}
def register_language(lang: Language):
    language_registry[lang.name] = lang

def get_language(language: Optional[Any]) -> Language:
    if language is None:
        return language_registry["a"]
    elif isinstance(language, Language):
        return language
    elif isinstance(language, str):
        if language in language_registry:
            return language_registry[language]
    raise ValueError(f"Invalid language: {language}")
