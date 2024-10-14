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

    def write_alias(self, a: "Alias"): # type: ignore
        self.write(f"{a.name} = ")
        self.write_type_ref(a.aliased_type)
        self.write("\n")

    def write_binop(self, b: exprs.Binop):
        self.write("(")
        self.write_expr(b.left)
        self.write(" ")
        self.write(b.operator.op)
        self.write(" ")
        self.write_expr(b.right)
        self.write(")")

    def write_constant(self, c: "Constant"): # type: ignore
        self.write(repr(c.value))

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
        self.write("# ")
        self.write(comment)
        self.write("\n")

    def write_loop(self, f: stmts.Loop):
        self.write(f"for (var {f.var}: ")
        self.write_type_ref(typs.int_type)
        self.write(f" = 0; {f.var} < ")
        self.write_expr(f.count)
        self.write(f"; {f.var}++) {{\n")
        for s in f.statements:
            self.write_node(s)
        self.write("}\n")

    def write_struct(self, s: typs.Struct):
        self.write(f"struct {s.name}:\n")
        for field in s.fields:
            self.write(f"    {field.name}: ")
            self.write_type_ref(field.field_type)
            self.write("\n")

    def write_function(self, f: funcs.Function):
        self.write(f"{f.name}(")
        ps = f.parameters
        for i, param in enumerate(ps):
            self.write(param.name)
            self.write(": ")
            self.write_type_ref(param.parameter_type)
            if i < len(ps) - 1:
                self.write(", ")
        self.write("): ")
        self.write_type_ref(f.return_type)
        self.write(" =")
        ss = f.statements
        if len(ss) == 0:
            self.write(" ...\n")
        elif len(ss) == 1 and ss[0].node_type == nodes.NodeType.RETURN:
            ret_val = ss[0].value
            if ret_val is None:
                self.write(" ()\n")
            else:
                self.write(" ")
                self.write_expr(ret_val)
                self.write("\n")
        else:
            for s in f.statements:
                self.write_node(s)

    def write_return(self, r: stmts.Return):
        self.write("return")
        if r.value is not None:
            self.write(" ")
            self.write_expr(r.value)

    def write_set(self, s: stmts.Set):
        self.write_expr(s.target)
        self.write(" = ")
        self.write_expr(s.value)
        self.write("\n")

    def write_support_node(self, n: "Node"): # type: ignore
        # Support not needed for A
        pass

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
        left = python_expr_to_alang_expr(expr.left)
        right = python_expr_to_alang_expr(expr.right)
        if op_name == "add":
            return left + right
        elif op_name == "sub":
            return left - right
        elif op_name == "mult":
            return left * right
        elif op_name == "div":
            return left / right
        elif op_name == "matmult":
            op_name = "matmul"
        return exprs.Binop(left, op_name, right)
    elif isinstance(expr, ast.Compare):
        if len(expr.ops) != 1:
            raise NotImplementedError(f"Unsupported number of comparison operators: {len(expr.ops)}")
        if len(expr.comparators) != 1:
            raise NotImplementedError(f"Unsupported number of comparators: {len(expr.comparators)}")
        op = expr.ops[0]
        if isinstance(op, ast.Eq):
            op_name = "=="
        elif isinstance(op, ast.NotEq):
            op_name = "!="
        elif isinstance(op, ast.Lt):
            op_name = "<"
        elif isinstance(op, ast.LtE):
            op_name = "<="
        elif isinstance(op, ast.Gt):
            op_name = ">"
        elif isinstance(op, ast.GtE):
            op_name = ">="
        else:
            raise NotImplementedError(f"Unsupported comparison operator: {type(op)}")
        left = python_expr_to_alang_expr(expr.left)
        right = python_expr_to_alang_expr(expr.comparators[0])
        return exprs.Binop(left, op_name, right)
            
    elif isinstance(expr, ast.Constant):
        return exprs.Constant(expr.value)
    else:
        raise NotImplementedError(f"Unsupported expression type: {type(expr)}")

a_lang = ALanguage()
register_language(a_lang)
