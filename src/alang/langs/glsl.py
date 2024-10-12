from typing import Optional, TextIO, Union
from langs.language import Language, register_language
from langs.c import CWriter

import exprs
import funcs
import typs

class GLSLWriter(CWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def get_type_name(self, t: typs.Type) -> str:
        if t is None:
            return "void"
        elif isinstance(t, typs.Integer):
            if t.bits == 32:
                if t.signed:
                    return "int"
                else:
                    return "uint"
            else:
                self.error(f"Integer type `{t.name}` not supported")
                return "int" if t.signed else "uint"
        elif isinstance(t, typs.Float):
            if t.bits == 32:
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
            if element_type_name == "float":
                return f"vec{n}"
            elif element_type_name == "double":
                return f"dvec{n}"
            elif element_type_name == "int":
                return f"ivec{n}"
            elif element_type_name == "uint":
                return f"uvec{n}"
        else:
            return t.name

class GLSLLanguage(Language):
    def __init__(self):
        super().__init__("glsl")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> GLSLWriter: # type: ignore
        return GLSLWriter(out, options)

glsl_lang = GLSLLanguage()
register_language(glsl_lang)
