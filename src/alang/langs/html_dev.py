"""GLSL https://www.khronos.org/opengl/wiki/OpenGL_Shading_Language"""

from typing import Optional, TextIO, Union
from langs.language import Language, register_language
from langs.writer import CodeWriter

import stmts
import typs
import funcs

def encode(str):
    return str.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

class HTMLWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)
        self.out_langs = ["wgsl", "js", "c", "metal", "glsl", "a"]

    def write_expr_stmt(self, e: stmts.ExprStmt):
        self.write_expr(e.expression)

    def write_index(self, i: "Index"): # type: ignore
        self.write_expr(i.base)
        self.write("[")
        for ri, r in enumerate(i.ranges):
            if ri > 0:
                self.write(", ")
            if r is None:
                self.write(":")
            else:
                self.write_expr(r)
        self.write("]")

    def write_line_comment(self, comment: str):
        self.write("<p>")
        self.write(encode(comment))
        self.write("</p>\n")

    def write_module(self, s: "mods.Module"): # type: ignore
        self.write(f"<html>\n")
        self.write(f"<head>\n")
        self.write(f"<title>{encode(s.name)}</title>\n")
        self.write(f"<style>\n")
        # Enable automatic dark mode
        self.write(f"html {{ color-scheme: light dark; font-family:Helvetica }}\n")
        self.write(f"#errors {{ color: #F88; }}\n")
        self.write(f"pre {{ overflow-x: auto; }}\n")
        self.write(f".code {{ background-color:rgba(128,128,128,0.25); margin:1em; padding: 1em; font-size:110%; }}\n")
        self.write(f"</style>\n")
        self.write(f"</head>\n")
        self.write(f"<body>\n")
        self.write(f"<h1>{encode(s.name)}</h1>\n")
        self.write(f"<ul id='errors'></ul>\n")
        for type in s.types:
            self.write_type_ui(type)
        for func in s.functions:
            self.write_function_ui(func)
        self.write(f"<script type='module'>\n")
        self.write(s.get_code("js", self.options))
        self.write("const wgslCode = `\n")
        self.write(s.get_code("wgsl", self.options))
        self.write("`;\n")
        self.write("const wgslLines = wgslCode.split('\\n');\n")
        self.write(f"async function main() {{\n")
        self.indent()
        self.write(f"const $errors = document.getElementById('errors');\n")
        self.write(f"const error = (m) => {{ $errors.appendChild(document.createElement('li')).textContent = m; }};\n")
        self.write(f"const adapter = await navigator.gpu.requestAdapter();\n")
        self.write(f"const device = await adapter.requestDevice();\n")
        self.write(f"const wgslModule = device.createShaderModule({{code: wgslCode}});\n")
        self.write(f"const wgslModuleInfo = await wgslModule.getCompilationInfo();\n")
        self.write("for (let m of wgslModuleInfo.messages) {\n")
        self.write("    console.log(m);\n")
        self.write("    const line = wgslLines[m.lineNum - 1];\n")
        self.write("    error(`WGSL: ${m.message} \"${line}\"`);\n")
        self.write("}\n")
        for type in s.types:
            self.write_type_ui_code(type)
        for func in s.functions:
            self.write_function_ui_code(func)
        self.dedent()
        self.write(f"}}\n")
        self.write(f"main();\n")
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

    def write_set(self, s: stmts.Set):
        self.write_expr(s.target)
        self.write(" = ")
        self.write_expr(s.value)

    def write_struct(self, s: typs.Struct):
        self.write_struct_ui(s)
        self.write_struct_ui_code(s)

    def write_struct_ui(self, s: typs.Struct):
        fs: list[typs.Field] = s.fields
        sl = s.layout
        n = len(fs)
        anno = self.options.struct_annotations
        enc_name = encode(s.name)
        self.write(f"<h2>{enc_name}</h2>\n")
        self.write(f"<code><pre>{encode(str(s))}</pre></code>\n")

    def write_struct_ui_code(self, s: typs.Struct):
        self.write(f"let test{s.name} = new {s.name}();\n")
        self.write(f"console.log(test{s.name});\n")
        self.write(f"let test{s.name}GPUBuffer = test{s.name}.createGPUBuffer(device);\n")
        self.write(f"console.log(test{s.name}GPUBuffer);\n")

    def write_function(self, f: funcs.Function):
        self.write_function_ui(f)
        self.write_function_ui_code(f)

    def write_function_ui(self, f: funcs.Function):
        enc_name = encode(f.name)
        self.write(f"<div style='display: block;'>\n")
        self.write(f"<h2>{enc_name}</h2>\n")
        for p in f.parameters:
            self.write_input_ui_for_type(p.name, f.name + "_" + p.name, p.resolved_type or p.parameter_type)
        if f.resolved_type is not None and not f.resolved_type.return_type.is_void:
            self.write_input_ui_for_type("RETURN", f.name + "_return", f.resolved_type.return_type)
        for lang in self.out_langs:
            self.write(f"<div class='code' style='max-width:40%;display:inline-block;vertical-align: top;'>\n")
            self.write(f"<h3>{lang}</h3>\n")
            self.write(f"<code><pre>{encode(f.get_code(lang, self.options))}</pre></code>\n")
            self.write(f"</div>\n")
        self.write(f"<code style='max-width:40%;display:inline-block;'><pre>{encode(str(f))}</pre></code>\n")
        self.write(f"</div>\n")

    def write_input_ui_for_type(self, name: str, id: str, t: "Type"): # type: ignore
        enc_name = encode(name)
        self.write(f"<div>\n")
        self.write(f"<label for='{id}'>{enc_name}</label>\n")
        if t.is_scalar:
            self.write(f"<input id='{id}' type='number'>\n")
        elif t.is_vector:
            axis_names = ["x", "y", "z", "w"]
            n_axes = t.num_elements
            for i in range(n_axes):
                axis_name = axis_names[i]
                self.write(f"<label for='{id}{axis_name}'>{axis_name}</label>\n")
        elif t.is_tensor and len(t.shape) == 2:
            self.write(f"<table id='{id}'>\n")
            nr, nc = t.shape
            for r in range(nr):
                self.write(f"<tr>\n")
                for c in range(nc):
                    self.write(f"<td><input id='{id}_{r}_{c}' type='number' value=0></td>\n")
                self.write(f"</tr>\n")
            self.write(f"</table>\n")
        else:
            self.write(f"<input id='{id}' type='text'>\n")
        self.write(f"</div>\n")

    def write_function_ui_code(self, f: funcs.Function):
        stage_and_auto = self.get_func_stage(f)
        if stage_and_auto is None:
            return
        self.writeln(f"try {{")
        self.indent()
        self.writeln(f"let {f.name}GPUTest = new {f.name}GPU(device, wgslModule);")
        self.writeln(f"await {f.name}GPUTest.exec();")
        self.dedent()
        self.writeln(f"}} catch (e) {{")
        self.indent()
        self.writeln(f"console.error(`{f.name}GPUTest`, e);")
        self.writeln(f"error(`{f.name}GPUTest: ${{e}}`);")
        self.dedent()
        self.writeln(f"}}")

    def write_support_node(self, n: "Node"): # type: ignore
        pass

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
