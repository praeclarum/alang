from typing import Optional, TextIO, Union

from langs.language import Language, register_language
from langs.writer import CodeWriter
import exprs
import funcs
import stmts
import typs

class CWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def write_binop(self, b: exprs.Binop):
        self.write("(")
        self.write_expr(b.left)
        self.write(" ")
        self.write(b.operator)
        self.write(" ")
        self.write_expr(b.right)
        self.write(")")

    def write_function(self, f: funcs.Function):
        self.write_type_ref(f.return_type)
        self.write(f" {f.name}(")
        ps = f.parameters
        for i, param in enumerate(ps):
            self.write_type_ref(param.parameter_type)
            self.write(f" {param.name}")
            if i < len(ps) - 1:
                self.write(", ")
        self.write(") {\n")
        for s in f.statements:
            self.write_statement(s)
        self.write("}\n")

    def write_return(self, r: stmts.Return):
        self.write("    return")
        if r.value is not None:
            self.write(" ")
            self.write_expr(r.value)
        self.write(";\n")

    def write_name(self, n: exprs.Name):
        self.write(n.name)

    def write_type_ref(self, t: typs.Type):
        self.write(self.get_type_name(t))

    def get_type_name(self, t: typs.Type) -> str:
        if t is None:
            return "void"
        elif isinstance(t, typs.Integer):
            tn = t.name
            if tn == "sbyte":
                return "int8_t"
            elif tn == "byte":
                return "uint8_t"
            elif tn == "int":
                return "int32_t"
            elif tn == "uint":
                return "uint32_t"
            elif tn == "long":
                return "int64_t"
            elif tn == "ulong":
                return "uint64_t"
            else:
                raise ValueError(f"Invalid integer type: {tn}")
        elif isinstance(t, typs.Float):
            tn = t.name
            if tn == "half":
                return "half"
            elif tn == "float":
                return "float"
            elif tn == "double":
                return "double"
            else:
                raise ValueError(f"Invalid float type: {tn}")
        elif isinstance(t, typs.Vector):
            n = t.size
            if n > 4 or n < 2:
                raise ValueError(f"Invalid vector size: {n}")
            element_type = self.get_type_name(t.element_type)
            return f"{element_type}{n}"
        else:
            return t.name


class CLanguage(Language):
    def __init__(self):
        super().__init__("c")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> CWriter: # type: ignore
        return CWriter(out, options)

c_lang = CLanguage()
register_language(c_lang)

