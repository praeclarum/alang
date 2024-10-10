import nodes
from nodes import Expression, ASTNode
import exprs

import ast

Code = str

def parse_expr(expr: Code) -> Expression:
    if expr is None:
        return None
    if isinstance(expr, ASTNode):
        return expr
    if isinstance(expr, str):
        ast_expr = ast.parse(expr).body[0].value
        return python_expr_to_alang_expr(ast_expr)
    return exprs.Constant(expr)

def python_expr_to_alang_expr(expr: ast.expr) -> Expression:
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
