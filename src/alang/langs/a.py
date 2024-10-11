from typing import TextIO, Union
from langs.language import Language, register_language
from langs.writer import CodeWriter

import ast
import nodes
import exprs
import typs

Code = str

class AWriter(CodeWriter):
    def __init__(self, out: Union[str, TextIO]):
        super().__init__(out)

    def write_struct(self, s: typs.Struct):
        self.write(f"struct {s.name}:\n")
        for field in s.fields:
            self.write(f"    {field.name}: ")
            self.write_type(field.field_type)
            self.write("\n")

    def write_type(self, t: typs.Type):
        self.write(t.name)

class ALanguage(Language):
    def __init__(self):
        super().__init__("a")

    def open_writer(self, out: Union[str, TextIO]) -> AWriter:
        return AWriter(out)

    def parse_expr(self, expr: Code):
        if expr is None:
            return None
        if isinstance(expr, nodes.ASTNode):
            return expr
        if isinstance(expr, str):
            ast_expr = ast.parse(expr).body[0].value
            return python_expr_to_alang_expr(ast_expr)
        return exprs.Constant(expr)

def python_expr_to_alang_expr(expr: ast.expr):
    if isinstance(expr, ast.Name):
        return exprs.Name(expr.id)
    elif isinstance(expr, ast.BinOp):
        op_class_name = expr.op.__class__.__name__
        return exprs.Binop(
            python_expr_to_alang_expr(expr.left),
            op_class_name,
            python_expr_to_alang_expr(expr.right)
        )
    elif isinstance(expr, ast.Constant):
        return exprs.Constant(expr.value)
    else:
        raise NotImplementedError(f"Unsupported expression type: {type(expr)}")

a_lang = ALanguage()
register_language(a_lang)
