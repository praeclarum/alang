from typing import Optional, TextIO, Union
import ast

from langs.language import Language, register_language
from langs.writer import CodeWriter
import nodes
import exprs
import typs
import funcs
import stmts

Code = str

class AWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        super().__init__(out, options)

    def write_binop(self, b: exprs.Binop):
        self.write("(")
        self.write_expr(b.left)
        self.write(" ")
        self.write(b.operator.op)
        self.write(" ")
        self.write_expr(b.right)
        self.write(")")

    def write_line_comment(self, comment: str):
        self.write("// ")
        self.write(comment)
        self.write("\n")

    def write_struct(self, s: typs.Struct):
        self.write(f"struct {s.name}:\n")
        for field in s.fields:
            self.write(f"    {field.name}: ")
            self.write_type_ref(field.field_type)
            self.write("\n")

    def write_function(self, f: funcs.Function):
        self.write(f"def {f.name}(")
        ps = f.parameters
        for i, param in enumerate(ps):
            self.write(param.name)
            self.write(": ")
            self.write_type_ref(param.parameter_type)
            if i < len(ps) - 1:
                self.write(", ")
        self.write("):\n")
        for s in f.statements:
            self.write_statement(s)

    def write_return(self, r: stmts.Return):
        self.write("    return")
        if r.value is not None:
            self.write(" ")
            self.write_expr(r.value)

    def write_name(self, n: exprs.Name):
        self.write(n.name)

    def write_type_ref(self, t: typs.Type):
        self.write(t.name)

class ALanguage(Language):
    def __init__(self):
        super().__init__("a")

    def open_writer(self, out: Union[str, TextIO], options: Optional["CodeOptions"]) -> AWriter: # type: ignore
        return AWriter(out, options)

    def parse_expr(self, expr: Code):
        if expr is None:
            return None
        if isinstance(expr, nodes.Node):
            return expr
        if isinstance(expr, str):
            ast_expr = ast.parse(expr).body[0].value
            return python_expr_to_alang_expr(ast_expr)
        return exprs.Constant(expr)

def python_expr_to_alang_expr(expr: ast.expr):
    if isinstance(expr, ast.Name):
        return exprs.Name(expr.id)
    elif isinstance(expr, ast.BinOp):
        op_name = expr.op.__class__.__name__.lower()
        if op_name == "mult":
            op_name = "mul"
        elif op_name == "matmult":
            op_name = "matmul"
        return exprs.Binop(
            python_expr_to_alang_expr(expr.left),
            op_name,
            python_expr_to_alang_expr(expr.right)
        )
    elif isinstance(expr, ast.Constant):
        return exprs.Constant(expr.value)
    else:
        raise NotImplementedError(f"Unsupported expression type: {type(expr)}")

a_lang = ALanguage()
register_language(a_lang)
