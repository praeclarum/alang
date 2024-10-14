from typing import Optional, TextIO, Union
from nodes import Expression, NodeType, Statement
from langs.language import Language, register_language
from langs.writer import CodeWriter

import typs
import funcs
import stmts
import exprs

class JSWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def write_alias(self, b: "Alias"): # type: ignore
        pass # No types in JS

    def write_binop(self, b: exprs.Binop):
        support_name = b.get_support_lib_function_name()
        if support_name is not None:
            self.write(support_name)
            self.write("(")
            self.write_expr(b.left)
            self.write(", ")
            self.write_expr(b.right)
            self.write(")")
        else:
            self.write("(")
            self.write_expr(b.left)
            self.write(" ")
            self.write(b.operator.op)
            self.write(" ")
            self.write_expr(b.right)
            self.write(")")

    def write_block(self, b: stmts.Block):
        self.write("{\n")
        self.indent()
        for s in b.statements:
            self.write_node(s)
        self.dedent()
        self.write("}\n")

    def write_constant(self, c: "Constant"): # type: ignore
        self.write(repr(c.value))

    def write_expr_stmt(self, e: stmts.ExprStmt):
        self.write_expr(e.expression)
        self.write(";\n")

    def write_function(self, f: funcs.Function):
        self.write_js_function(f)
        s = self.get_func_stage(f)
        if s is not None:
            self.write_gpu_function(f, s)

    def write_js_function(self, f: funcs.Function):
        self.write(f"function {f.name}(")
        for i, param in enumerate(f.parameters):
            if i > 0:
                self.write(", ")
            self.write(f"{param.name}/*: {self.get_typed_name(param.parameter_type)}*/")
        self.write(") ")
        self.write_block(f)

    def write_gpu_function(self, original_f: funcs.Function, stage_and_f: tuple[str, funcs.Function]):
        stage, f = stage_and_f
        pts = [(p.resolved_type or p.parameter_type) for p in f.parameters]
        self.write(f"class {original_f.name}GPU {{\n")
        self.indent()
        self.writeln(f"constructor(device, shaderModule) {{")
        self.indent()
        self.writeln("this.device = device;")
        self.writeln(f"console.log('Creating GPU function {f.name}');")
        for i, param in enumerate(f.parameters):
            self.writeln(f"self.{param.name} = null; // {self.get_typed_name(pts[i])}")
        self.writeln("this.computePipeline = device.createComputePipeline({")
        self.indent()
        self.writeln(f"label: '{f.name}_pipeline',")
        self.writeln("layout: 'auto',")
        self.writeln("compute: {")
        self.indent()
        self.writeln("module: shaderModule,")
        self.writeln(f"entryPoint: '{f.name}'")
        self.dedent()
        self.writeln("}")
        self.dedent()
        self.writeln("});")
        self.writeln("const bindGroupLayout = this.computePipeline.getBindGroupLayout(0);")
        self.writeln("console.log('Created GPU function pipeline', this.computePipeline);")
        self.writeln("this.bindGroup = device.createBindGroup({")
        self.indent()
        self.writeln("layout: bindGroupLayout,")
        self.writeln("entries: [")
        self.indent()
        for i, param in enumerate(f.parameters):
            break
            self.writeln("{")
            self.indent()
            self.writeln(f"binding: {i},")
            self.writeln(f"resource: this.{param.name}.gpuBuffer")
            self.dedent()
            self.writeln("},")
        self.dedent()
        self.writeln("]")
        self.dedent()
        self.writeln("});")
        self.writeln("console.log('Created GPU function bind group', this.bindGroup);")
        self.dedent()
        self.writeln("}")
        self.write("encode() {")
        self.indent()
        self.writeln(f"console.log('Encoding GPU function {f.name}');")
        self.writeln("const commandEncoder = this.device.createCommandEncoder();")
        self.writeln(f"const passEncoder = commandEncoder.beginComputePass({{label:'{f.name}_pass'}});")
        self.writeln("passEncoder.setPipeline(this.computePipeline);")
        self.writeln("passEncoder.setBindGroup(0, this.bindGroup);")
        self.writeln("passEncoder.dispatchWorkgroups(1);")
        self.writeln("passEncoder.end();")
        self.writeln(f"return commandEncoder.finish({{label:'{f.name}_command'}});")
        self.dedent()
        self.writeln("}")
        self.write("exec() {")
        self.indent()
        self.writeln(f"console.log('Executing GPU function {f.name}');")
        self.writeln("const commandBuffer = this.encode();")
        self.writeln("console.log('Executing GPU function command buffer', commandBuffer);")
        self.writeln("this.device.queue.submit([commandBuffer]);")
        self.dedent()
        self.writeln("}")
        self.dedent()
        self.write("}\n")

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

    def write_loop(self, f: stmts.Loop):
        self.write("for (let")
        self.write(f" {f.var} = 0; {f.var} < ")
        self.write_expr(f.count)
        self.write(f"; {f.var}++) {{\n")
        self.indent()
        for s in f.statements:
            self.write_node(s)
        self.dedent()
        self.write("}\n")

    def write_line_comment(self, comment: str):
        self.write("// ")
        self.write(comment)
        self.write("\n")

    def write_set(self, s: stmts.Set):
        self.write_expr(s.target)
        self.write(" = ")
        self.write_expr(s.value)
        self.write(";\n")

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
            elif field_type.is_tensor:
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

    def write_return(self, s: stmts.Return):
        self.write(f"return")
        rv = s.value
        if rv is not None:
            self.write(" ")
            self.write_expr(rv)
        self.write(";\n")

    def write_name(self, s: exprs.Name):
        self.write(s.name)

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
