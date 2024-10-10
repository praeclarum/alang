from typing import TextIO, Union

wrote_vec_def = set()
wrote_mat_def = set()
wrote_mm = set()

class CodeWriter:
    def __init__(self, path_or_io: Union[str, TextIO]):
        if type(path_or_io) is str:
            self.out = open(path_or_io, "w")
            self.owner = True
        else:
            self.out = path_or_io
            self.owner = False
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    def write(self, s: str):
        self.out.write(s)
    def close(self):
        if self.owner and self.out is not None:
            self.out.close()
            self.out = None
            self.owner = False

def open_writer(out: Union[str, TextIO]) -> CodeWriter:
    return CodeWriter(out)

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
