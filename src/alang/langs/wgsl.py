"""WGSL https://www.w3.org/TR/WGSL/"""

from typing import Optional, TextIO, Union

from langs.language import Language, register_language
from langs.writer import CodeWriter
import exprs
import funcs
import nodes
import stmts
import typs

class WGSLWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def write_alias(self, a: "Alias"): # type: ignore
        self.write(f"alias {a.name} = ")
        self.write_type_ref(a.aliased_type)
        self.write(";\n")

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

    def write_block(self, f: stmts.Block):
        self.writeln("{")
        self.indent()
        for v in f.variables:
            self.write_variable(v)
        for s in f.statements:
            self.write_node(s)
        self.dedent()
        self.writeln("}")

    def write_constant(self, c: "Constant"): # type: ignore
        self.write(repr(c.value))

    def write_expr_stmt(self, e: stmts.ExprStmt):
        self.write_expr(e.expression)
        self.write(";\n")

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
        self.write(f"for (var {f.var}: ")
        self.write_type_ref(typs.int_type)
        self.write(f" = 0; {f.var} < ")
        self.write_expr(f.count)
        self.writeln(f"; {f.var}++) {{")
        self.indent()
        for s in f.statements:
            self.write_node(s)
        self.dedent()
        self.writeln("}")

    def write_funcall(self, c: exprs.Funcall):
        f = c.func
        if f is None:
            self.write_error_value("Missing function")
            return
        if f.node_type == nodes.NodeType.FUNCTION:
            self.write(f.name)
        else:
            self.write_expr(f)
        self.write("(")
        for i, arg in enumerate(c.args):
            if i > 0:
                self.write(", ")
            self.write_expr(arg)
        self.write(")")

    def write_function(self, f: funcs.Function):
        stage_and_auto = self.get_func_stage(f)
        if f.stage is not None:
            self.writeln(f"@{f.stage}")
        self.write(f"fn {f.name}(")
        ps = f.parameters
        for i, param in enumerate(ps):
            if param.location is not None:
                self.write(f"@location({param.location}) ")
            self.write(f"{param.name}: ")
            self.write_type_ref(param.parameter_type)
            if i < len(ps) - 1:
                self.write(", ")
        self.write(") ")
        if not f.return_type.is_void:
            self.write("-> ")
            self.write_type_ref(f.return_type)
            self.write(" ")
        self.write_block(f)
        if stage_and_auto is not None:
            self.write_auto_entry_point_function(f, *stage_and_auto)

    def write_auto_entry_point_function(self, original_f: funcs.Function, stage: str, f: funcs.Function):
        pts = original_f.resolved_type.parameter_types
        for i, p in enumerate(original_f.parameters):
            self.write(f"@group(0) @binding({i}) var<storage> {p.name}_auto_compute: ")
            self.write_type_ref(pts[i])
            self.write(";\n")
        workgroup_size = f.workgroup_size or 1
        self.writeln(f"@{stage} @workgroup_size({workgroup_size})")
        self.writeln(f"fn {f.name}() {{")
        self.indent()
        self.write(f"{original_f.name}(")
        for i, p in enumerate(original_f.parameters):
            if i > 0:
                self.write(", ")
            self.write(p.name + "_auto_compute")
        self.writeln(");")
        self.dedent()
        self.writeln("}")

    def write_line_comment(self, comment: str):
        self.write("// ")
        self.write(comment)
        self.write("\n")

    def write_name(self, n: exprs.Name):
        self.write(n.name)

    def write_return(self, r: stmts.Return):
        self.write("return")
        if r.value is not None:
            self.write(" ")
            self.write_expr(r.value)
        self.write(";\n")

    def write_set(self, s: stmts.Set):
        self.write_expr(s.target)
        self.write(" = ")
        self.write_expr(s.value)
        self.write(";\n")

    def write_struct(self, s: typs.Struct):
        fs = s.fields
        sl = s.layout
        n = len(fs)
        anno_col = 46
        anno = self.options.struct_annotations
        self.write(f"struct {s.name} {{")
        def write_anno(o, a, s, text_len):
            if anno:
                tab = " " * max(anno_col - text_len, 1)
                o_text = ""
                if o is not None:
                    o_text = f"offset({o})"
                a_text = f"align({a})"
                self.write(f"{tab}// {o_text.ljust(12)}{a_text.ljust(10)}size({s})")
        write_anno(None, sl.align, sl.byte_size, len(s.name) + 8)
        self.write("\n")
        for i, field in enumerate(fs):
            field_type = self.get_type_name(field.field_type)
            self.write(f"    {field.name}: {field_type}")
            text_len = len(field.name) + len(field_type) + 5
            if i < n - 1:
                self.write(",")
                text_len += 1
            fl = sl.fields[i]
            write_anno(fl.offset, fl.align, fl.byte_size, text_len)
            self.write("\n")
        self.write("}\n")

    def write_type_ref(self, t: typs.Type):
        self.write(self.get_type_name(t))

    def write_variable(self, v: nodes.Variable):
        self.write("var")
        if v.address_space is not None and v.address_space != "function":
            self.write(f"<{v.address_space}")
            if v.access_mode is not None and v.address_space == "storage":
                self.write(", ")
                self.write(v.access_mode)
            self.write("> ")
        else:
            self.write(" ")
        self.write(v.name)
        self.write(": ")
        self.write_type_ref(v.resolved_type or v.variable_type)
        self.write(";\n")

    def get_type_name(self, t: typs.Type) -> str:
        if t is None:
            return "void"
        elif isinstance(t, typs.Array):
            n = t.num_elements
            element_type = self.get_type_name(t.element_type)
            return f"array<{element_type}, {n}>" if n is not None else f"array<{element_type}>"
        elif isinstance(t, typs.Integer):
            tn = t.name
            if tn == "sbyte":
                return "i8"
            elif tn == "byte":
                return "u8"
            elif tn == "int":
                return "i32"
            elif tn == "uint":
                return "u32"
            elif tn == "long":
                return "i64"
            elif tn == "ulong":
                return "u64"
            else:
                raise ValueError(f"Invalid integer type: {tn}")
        elif isinstance(t, typs.Float):
            tn = t.name
            if tn == "half":
                return "f16"
            elif tn == "float":
                return "f32"
            elif tn == "double":
                return "f64"
            else:
                raise ValueError(f"Invalid float type: {tn}")
        elif isinstance(t, typs.Vector):
            n = t.size
            if n == 2:
                vec_type = "vec2"
            elif n == 3:
                vec_type = "vec3"
            elif n == 4:
                vec_type = "vec4"
            else:
                raise ValueError(f"Invalid vector size: {n}")
            element_type = self.get_type_name(t.element_type)
            return f"{vec_type}<{element_type}>"
        elif isinstance(t, typs.Pointer):
            element_type = self.get_type_name(t.element_type)
            address_space = t.address_space
            if address_space is None:
                address_space = "function"
            if t.access_mode is not None:
                return f"ptr<{address_space}, {element_type}, {t.access_mode}>"
            else:
                return f"ptr<{address_space}, {element_type}>"
        else:
            return t.name

class WGSLLanguage(Language):
    def __init__(self):
        super().__init__("wgsl")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> WGSLWriter: # type: ignore
        return WGSLWriter(out, options)

wgsl_lang = WGSLLanguage()
register_language(wgsl_lang)




wrote_vec_def = set()
wrote_mat_def = set()
wrote_mm = set()

def get_mat_type(shape) -> str:
    r, c = shape
    if c == 1 or r == 1:
        n = max(r, c)
        if n == 1:
            return "f32"
        elif n <= 4:
            return f"vec{n}<f32>"
        else:
            return f"vec{n}f"
    else:
        if r <= 4 and c <= 4:
            return f"mat{r}x{c}<f32>"
        else:
            return f"mat{r}x{c}f"

def get_mm_name(a_shape, b_shape, out):
    global wrote_mm
    a_r, a_c = a_shape
    b_r, b_c = b_shape
    if a_c != b_r:
        raise ValueError(f"Matrices can't be multiplied: {a_shape} x {b_shape}")
    a_type = get_mat_type(a_shape).replace("<f32>", "f")
    b_type = get_mat_type(b_shape).replace("<f32>", "f")
    name = f"mul_{a_type}_{b_type}"
    if name not in wrote_mm:
        write_mm_func(name, a_shape, b_shape, out)
    return name

def write_vec_defs(r, out):
    global wrote_vec_def
    if r <= 4 or r in wrote_vec_def:
        return
    wrote_vec_def.add(r)
    vec_type = get_mat_type((r, 1))
    num_vec4s = r // 4
    rem_vec_len = r % 4
    # Data Type
    out.write(f"struct {vec_type} {{\n")
    for i in range(num_vec4s):
        out.write(f"    row{i*4}: vec4<f32>")
        if i < num_vec4s - 1 or rem_vec_len > 0:
            out.write(",\n")
        else:
            out.write("\n")
    if rem_vec_len > 0:
        out.write(f"    row{num_vec4s*4}: vec{rem_vec_len}<f32>;\n")
    out.write("};\n")
    # Dot Product
    out.write(f"fn dot{r}(a: {vec_type}, b: {vec_type}) -> f32 {{\n")
    out.write("    return ")
    for i in range(num_vec4s):
        out.write(f"dot(a.row{i*4}, b.row{i*4})")
        if i < num_vec4s - 1 or rem_vec_len > 0:
            out.write(" + ")
    if rem_vec_len > 0:
        out.write(f"dot(a.row{num_vec4s*4}, b.row{num_vec4s*4})")
    out.write(";\n")
    out.write("}\n")

def write_mat_defs(r, c, out):
    global wrote_mat_def
    if r <= 4 and c <= 4 or (r, c) in wrote_mat_def:
        return
    wrote_mat_def.add((r, c))
    mat_type = get_mat_type((r, c))
    col_type = get_mat_type((r, 1))
    # Data Type
    out.write(f"struct {mat_type} {{\n")
    for col in range(c):
        out.write(f"    col{col}: {col_type}")
        if col < c - 1:
            out.write(",\n")
        else:
            out.write("\n")
    out.write("};\n")

def write_mat_row(name, shape, row, out):
    r, c = shape
    if r == 1 or c == 1:
        out.write(f"{name}")
        return
    row_type = get_mat_type((1, c))
    out.write(f"{row_type}(")
    for col in range(c):
        out.write(f"{name}[{row}, {col}]")
        if col < c - 1:
            out.write(", ")
    out.write(")")

def write_mat_col(name, shape, col, out):
    r, c = shape
    if r == 1 or c == 1:
        out.write(f"{name}")
        return
    col_type = get_mat_type((r, 1))
    if r > 4 or c > 4:
        out.write(f"{name}.col{col}")
        return
    out.write(f"{name}[{col}]")

def write_mm_func(name, a_shape, b_shape, out):
    global wrote_mm
    wrote_mm.add(name)
    a_r, a_c = a_shape
    b_r, b_c = b_shape
    if a_c != b_r:
        raise ValueError(f"Matrices can't be multiplied: {a_shape} x {b_shape}")
    out_r, out_c = a_r, b_c
    a_type = get_mat_type(a_shape)
    b_type = get_mat_type(b_shape)
    out_type = get_mat_type((out_r, out_c))
    out_col_type = get_mat_type((out_r, 1))
    dot_name = "dot"
    if a_c > 4:
        write_vec_defs(a_c, out)
        dot_name = f"dot{a_c}"
    out.write(f"fn {name}(a: {a_type}, b: {b_type}) -> {out_type} {{\n")
    # Calculate the MM one column at a time
    for out_col in range(b_c):
        out.write(f"    let col{out_col}: {out_col_type} = ")
        if out_col_type != "f32":
            out.write(f"{out_col_type}(")
        for out_row in range(a_r):
            out.write(f"{dot_name}(")
            write_mat_row("a", a_shape, out_row, out)
            out.write(", ")
            write_mat_col("b", b_shape, out_col, out)
            out.write(")")
            if out_row < a_r - 1:
                out.write(", ")
        if out_col_type == "f32":
            out.write(";\n")
        else:
            out.write(");\n")
    # Combine the columns into the output matrix
    if out_r == 1 and out_c == 1:
        out.write("    return col0;\n")
    else:
        out.write(f"    return {out_type}(")
        for out_col in range(b_c):
            out.write(f"col{out_col}")
            if out_col < b_c - 1:
                out.write(", ")
        out.write(");\n")
    out.write("}\n")

def write_vec(name, vec, out):
    r = vec.shape[0]
    vec_type = get_mat_type((r, 1))
    if name is not None:
        out.write(f"const {name}: {vec_type} = ")
    if r > 1:
        out.write(f"{vec_type}(")
    if r <= 4:
        for row in range(r):
            out.write(f"{vec[row]:.9f}")
            if row < r - 1:
                out.write(", ")
    else:
        num_vec4s = r // 4
        rem_vec_len = r % 4
        for i in range(num_vec4s):
            out.write("\n    ")
            write_vec(None, vec[i*4:(i+1)*4], out)
            if i < num_vec4s - 1 or rem_vec_len > 0:
                out.write(", ")
        if rem_vec_len > 0:
            out.write("\n    ")
            write_vec(None, vec[num_vec4s*4:], out)
    if r > 1:
        out.write(")")
    if name is not None:
        out.write(";\n")

def write_mat(name, mat, out):
    r, c = mat.shape
    if c == 1:
        write_vec(name, mat[:, 0], out)
    else:
        matType = get_mat_type((r, c))
        write_mat_defs(r, c, out)
        out.write(f"const {name}: {matType} = {matType}(\n")
        for col in range(c):
            write_vec(None, mat[:, col], out)
            if col < c - 1:
                out.write(",\n")
        out.write("\n);\n")
