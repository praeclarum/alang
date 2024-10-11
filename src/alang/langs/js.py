from typing import Optional, TextIO, Union
from langs.language import Language, register_language
from langs.writer import CodeWriter

import typs

class JSWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def write_struct(self, s: typs.Struct):
        fs = s.fields
        sl = s.layout
        n = len(fs)
        anno_col = 46
        anno = self.options.struct_annotations
        def write_anno(o, a, s, text_len):
            if anno:
                tab = " " * max(anno_col - text_len, 1)
                o_text = ""
                if o is not None:
                    o_text = f"offset({o})"
                a_text = f"align({a})"
                self.write(f"{tab}// {o_text.ljust(12)}{a_text.ljust(10)}size({s})")
        self.write(f"class {s.name} {{")
        write_anno(None, sl.align, sl.byte_size, len(s.name) + 8)
        self.write("\n")
        self.write(f"    constructor(buffer, byteOffset, byteLength) {{\n")
        self.write(f"        byteOffset = byteOffset || 0;\n")
        self.write(f"        byteLength = byteLength || {sl.byte_size};\n")
        self.write(f"        if (byteLength < {sl.byte_size}) throw new Error(`Buffer too small. \"{s.name}\" requires at least {sl.byte_size} bytes, got ${{byteLength}}`);\n")
        self.write(f"        if (buffer instanceof ArrayBuffer) {{\n")
        self.write(f"            this.buffer = buffer;\n")
        self.write(f"        }} else {{\n")
        self.write(f"            this.buffer = new ArrayBuffer(byteLength);\n")
        self.write(f"            byteOffset = 0;\n")
        self.write(f"        }}\n")
        self.write(f"        if (byteOffset + byteLength >= this.buffer.byteLength) throw new Error(`Buffer overflow. \"{s.name}\" requires ${{byteLength}} bytes starting at ${{byteOffset}}, but the buffer is only ${{this.buffer.byteLength}} bytes long`);\n")
        self.write(f"        this.view = new DataView(this.buffer, byteOffset, byteLength);\n")
        self.write(f"    }}\n")
        for i, field in enumerate(fs):
            field_type = self.get_typed_name(field.field_type)
            # self.write(f"        this.{field.name} = new DataView {field_type}")
            text_len = len(field.name) + len(field_type) + 5
            fl = sl.fields[i]
            # write_anno(fl.offset, fl.align, fl.byte_size, text_len)
            # self.write("\n")
        self.write("}\n")

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
                return "BigInt"
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

class JSLanguage(Language):
    def __init__(self):
        super().__init__("js")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> JSWriter: # type: ignore
        return JSWriter(out, options)

js_lang = JSLanguage()
register_language(js_lang)
