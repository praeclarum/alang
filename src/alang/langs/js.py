from typing import Optional, TextIO, Union
from langs.language import Language, register_language
from langs.writer import CodeWriter
import modules

import typs

class JSWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def write_module(self, s: modules.Module):
        for type in s.types:
            self.write_type(type)

    def write_type(self, t: typs.Type):
        if isinstance(t, typs.Struct):
            self.write_struct(t)
        else:
            self.write(f"    // {t.name}\n")

    def write_struct(self, s: typs.Struct):
        fs: list[typs.Field] = s.fields
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
        is_scalar_array = [False] * n
        scalar_array_num_elements = [0] * n
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
        self.write(f"        if (byteOffset + byteLength > this.buffer.byteLength) throw new Error(`Buffer overflow. \"{s.name}\" requires ${{byteLength}} bytes starting at ${{byteOffset}}, but the buffer is only ${{this.buffer.byteLength}} bytes long`);\n")
        self.write(f"        this.view = new DataView(this.buffer, byteOffset, byteLength);\n")
        self.write(f"        this.byteLength = byteLength;\n")
        self.write(f"        this.gpuBuffer = null;\n")
        self.write(f"        this.isDirty = false;\n")
        self.write(f"        this.dirtyBegin = 0;\n")
        self.write(f"        this.dirtyEnd = 0;\n")
        for i, field in enumerate(fs):
            field_type: typs.Type = field.field_type
            if field_type.is_array:
                is_scalar_array[i] = field_type.element_type.is_scalar
                scalar_array_num_elements[i] = field_type.num_elements
            elif field_type.is_vector:
                is_scalar_array[i] = True
                scalar_array_num_elements[i] = field_type.size
            if is_scalar_array[i]:
                element_type_name = self.get_typed_name(field_type.element_type)
                self.write(f"        this.{field.name}Array = new {element_type_name}Array(this.buffer, byteOffset + {sl.fields[i].offset}, {scalar_array_num_elements[i]});\n")
        self.write(f"    }}\n")
        self.write(f"    dirty(begin, end) {{\n")
        self.write(f"        if (begin === undefined || end === undefined) {{ begin = 0; end = this.byteLength; }}\n")
        self.write(f"        if (this.isDirty) {{ this.dirtyBegin = Math.min(this.dirtyBegin, begin); this.dirtyEnd = Math.max(this.dirtyEnd, end); }}\n")
        self.write(f"        else {{ this.dirtyBegin = begin; this.dirtyEnd = end; }}\n")
        self.write(f"        this.isDirty = true;\n")
        self.write(f"    }}\n")
        self.write(f"    createGPUBuffer(device, usage) {{\n")
        self.write(f"        usage = usage || (GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST);\n")
        self.write(f"        this.gpuBuffer = device.createBuffer({{ size: Math.max(this.byteLength, 256), usage: usage, label: \"{s.name}\", mappedAtCreation: false }});\n")
        self.write(f"        device.queue.writeBuffer(this.gpuBuffer, 0, this.buffer, this.view.byteOffset, this.byteLength);\n")
        self.write(f"        this.isDirty = false;\n")
        self.write(f"        return this.gpuBuffer;\n")
        self.write(f"    }}\n")
        for i, field in enumerate(fs):
            field_type = field.field_type
            if field_type.is_scalar:
                field_type_name = self.get_typed_name(field_type)
                self.write(f"    get {field.name}() {{ return this.view.get{field_type_name}({sl.fields[i].offset}); }}\n")
                self.write(f"    set {field.name}(value) {{ return this.view.set{field_type_name}({sl.fields[i].offset}, value); this.dirty({sl.fields[i].offset}, {sl.fields[i].offset + sl.fields[i].byte_size}); }}\n")
            elif is_scalar_array[i]:
                self.write(f"    get {field.name}() {{ return this.{field.name}Array; }}\n")
                self.write(f"    set {field.name}(value) {{ this.{field.name}Array.set(value); this.dirty({sl.fields[i].offset}, {sl.fields[i].offset + sl.fields[i].byte_size}); }}\n")
            else:
                raise NotImplementedError(f"Field type {field_type} not implemented")
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

class JSLanguage(Language):
    def __init__(self):
        super().__init__("js")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> JSWriter: # type: ignore
        return JSWriter(out, options)

js_lang = JSLanguage()
register_language(js_lang)
