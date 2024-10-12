"""Metal https://developer.apple.com/metal/Metal-Shading-Language-Specification.pdf"""

from typing import Optional, TextIO, Union
from langs.language import Language, register_language
from langs.c import CWriter

import exprs
import funcs
import typs

class MetalWriter(CWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def get_type_name(self, t: typs.Type) -> str:
        if t is None:
            self.error(f"Unresolved type in output")
            return "void"
        elif isinstance(t, typs.Integer):
            if t.bits == 8:
                return "char" if t.signed else "uchar"
            elif t.bits == 16:
                return "short" if t.signed else "ushort"
            elif t.bits == 32:
                return "int" if t.signed else "uint"
            elif t.bits == 64:
                return "long" if t.signed else "ulong"
            else:
                self.error(f"Integer type `{t.name}` not supported")
                return "int" if t.signed else "uint"
        elif isinstance(t, typs.Float):
            if t.bits == 16:
                return "half"
            elif t.bits == 32:
                return "float"
            elif t.bits == 64:
                return "double"
            else:
                self.error(f"Float type `{t.name}` not supported")
                return "float"
        elif isinstance(t, typs.Vector):
            n = t.size
            if n > 4 or n < 2:
                self.error(f"Invalid vector size: {n}")
                n = 4
            element_type_name = self.get_type_name(t.element_type).name
            return f"{element_type_name}{n}"
        else:
            return t.name

class MetalLanguage(Language):
    def __init__(self):
        super().__init__("metal")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> MetalWriter: # type: ignore
        return MetalWriter(out, options)

metal_lang = MetalLanguage()
register_language(metal_lang)
