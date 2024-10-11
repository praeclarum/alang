from typing import Optional, TextIO, Union
import modules
from langs.language import Language, register_language
from langs.writer import CodeWriter

import typs

def encode(str):
    return str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class HTMLWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def write_module(self, s: modules.Module):
        self.write(f"<html>\n")
        self.write(f"<head>\n")
        self.write(f"<title>{encode(s.name)}</title>\n")
        self.write(f"</head>\n")
        self.write(f"<body>\n")
        for type in s.types:
            self.write_type_ui(type)
        self.write(f"<script type='module'>\n")
        self.write(s.get_code("js", self.options))
        for type in s.types:
            self.write_type_ui_code(type)
        self.write(f"</script>\n")
        self.write(f"</body>\n")
        self.write(f"</html>\n")

    def write_type(self, t: typs.Type):
        self.write_type_ui(t)
        self.write_type_ui_code(t)

    def write_type_ui(self, t: typs.Type):
        if isinstance(t, typs.Struct):
            self.write_struct_ui(t)
        else:
            self.write(f"<h2>{encode(t.name)}</h2>\n")
            self.write(f"<code><pre>{encode(str(t))}</pre></code>\n")

    def write_type_ui_code(self, t: typs.Type):
        if isinstance(t, typs.Struct):
            self.write_struct_ui_code(t)
        else:
            pass

    def write_struct(self, s: typs.Struct):
        self.write_struct_ui(s)
        self.write_struct_ui_code(s)

    def write_struct_ui_code(self, s: typs.Struct):
        self.write(f"let test{s.name} = new {s.name}();\n")
        self.write(f"console.log(test{s.name});\n")

    def write_struct_ui(self, s: typs.Struct):
        fs: list[typs.Field] = s.fields
        sl = s.layout
        n = len(fs)
        anno = self.options.struct_annotations
        enc_name = encode(s.name)
        self.write(f"<h2>{enc_name}</h2>\n")
        self.write(f"<code><pre>{encode(str(s))}</pre></code>\n")

    def get_typed_name(self, t: typs.Type) -> str:
        if isinstance(t, typs.Integer):
            tn = t.name
            if tn == "sbyte":
                return "Int8"
            elif tn == "byte":
                return "UInt8"
            elif tn == "int":
                return "Int32"
            elif tn == "uint":
                return "UInt32"
            elif tn == "long":
                return "BigInt64"
            elif tn == "ulong":
                return "BigUint64"
            else:
                raise ValueError(f"Invalid integer type: {tn}")
        elif isinstance(t, typs.Float):
            tn = t.name
            if tn == "half":
                return "Float16"
            elif tn == "float":
                return "Float32"
            elif tn == "double":
                return "Float64"
            else:
                raise ValueError(f"Invalid float type: {tn}")
        elif isinstance(t, typs.Vector):
            return self.get_typed_array_name(t.element_type)
        else:
            return t.name
        
    def get_typed_array_name(self, t: typs.Type) -> str:
        return f"{self.get_typed_name(t)}Array"

    def get_js_name(self, t: typs.Type) -> str:
        if isinstance(t, typs.Integer):
            return "number"
        elif isinstance(t, typs.Float):
            return "number"
        elif isinstance(t, typs.Vector):
            return self.get_typed_array_name(t.element_type)
        elif isinstance(t, typs.Array):
            raise NotImplementedError("Arrays not implemented")
        else:
            return t.name

class HTMLLanguage(Language):
    def __init__(self):
        super().__init__("html")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> HTMLWriter: # type: ignore
        return HTMLWriter(out, options)

html_lang = HTMLLanguage()
register_language(html_lang)
