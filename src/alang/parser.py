from nodes import Expression
import ast
import expressions as exprs

Code = str

def parse_expr(expr: Code) -> Expression:
    ast_expr = ast.parse(expr).body[0].value
    return python_expr_to_alang_expr(ast_expr)

def python_expr_to_alang_expr(expr: ast.expr) -> Expression:
    if isinstance(expr, ast.Name):
        return exprs.Name(expr.id)
    else:
        raise NotImplementedError(f"Unsupported expression type: {type(expr)}")
