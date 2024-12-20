from typing import Optional

from alang.langs.writer import CodeWriter
from alang.nodes import Expression, Node, NodeAttr, NodeLink, NodeLinks, NodeType

import alang.compiler as compiler
import alang.funcs as funcs
import alang.stmts as stmts
import alang.typs as typs

class Attribute(Expression):
    target = NodeLink()
    name = NodeAttr()
    def __init__(self, target: Expression, name: str):
        super().__init__(NodeType.ATTRIBUTE)
        self.target = parse_expr(target)
        self.name = name
    def _get_precedence(self):
        return 100
    def resolve_type(self, diags: compiler.Diagnostics) -> typs.Type:
        bt: typs.Type = self.target.resolved_type
        if bt is None:
            return None
        return bt.get_attribute_type(self.name)

class Name(Expression):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__(NodeType.NAME)
        self.name = name
        self.resolved_node: Node = None
    def _get_precedence(self):
        return 100
    def resolve_type(self, diags: compiler.Diagnostics) -> typs.Type:
        if self.resolved_node is None:
            return None
        return self.resolved_node.resolved_type

class BinopOp:
    def __init__(self, name: str, op: str, precedence: int = 0, left_assoc: bool = True):
        self.name = name
        self.op = op
        self.precedence = precedence
        self.left_assoc = left_assoc
    def __str__(self):
        return self.op
    def __repr__(self):
        return repr(self.op)

bops = [
    BinopOp("mul", "*", precedence=14),
    BinopOp("matmul", "@", precedence=14),
    BinopOp("div", "/", precedence=14),
    BinopOp("mod", "%", precedence=14),
    BinopOp("add", "+", precedence=13),
    BinopOp("sub", "-", precedence=13),
    BinopOp("shl", "<<", precedence=12),
    BinopOp("shr", ">>", precedence=12),
    BinopOp("lt", "<", precedence=11),
    BinopOp("le", "<=", precedence=11),
    BinopOp("gt", ">", precedence=11),
    BinopOp("ge", ">=", precedence=11),
    BinopOp("eq", "==", precedence=10),
    BinopOp("ne", "!=", precedence=10),
    BinopOp("band", "&", precedence=9),
    BinopOp("xor", "^", precedence=8),
    BinopOp("bor", "|", precedence=7),
    BinopOp("and", "&&", precedence=6),
    BinopOp("or", "||", precedence=5),
]
bop_from_name = {bop.name: bop for bop in bops}
bop_from_op = {bop.op: bop for bop in bops}
    
class Binop(Expression):
    left = NodeLink()
    right = NodeLink()
    operator = NodeAttr()
    def __init__(self, left: Expression, operator: str, right: Expression):
        super().__init__(NodeType.BINOP)
        if operator in bop_from_name:
            self.operator = bop_from_name[operator]
        elif operator in bop_from_op:
            self.operator = bop_from_op[operator]
        else:
            raise Exception(f"Unknown operator: {operator}")
        self.left = parse_expr(left)
        self.right = parse_expr(right)
    def _get_precedence(self):
        return self.operator.precedence
    def resolve_type(self, diags: compiler.Diagnostics) -> typs.Type:
        lt: typs.Type = self.left.resolved_type
        rt: typs.Type = self.right.resolved_type
        if lt is None or rt is None:
            return None
        if not lt.is_algebraic:
            diags.error(f"Not an algebraic type", self.left)
            return None
        if not rt.is_algebraic:
            diags.error(f"Not an algebraic type", self.right)
            return None
        opn = self.operator.name
        if opn == "matmul":
            if lt.is_tensor and rt.is_tensor:
                return lt @ rt
            else:
                return None
        elif opn in ["add", "sub", "mul", "div", "mod"]:
            return lt
        elif opn in ["shl", "shr", "band", "bor"]:
            return lt
        else:
            diags.error(f"Binary operator {self.operator.op} type resolution not supported")
            return lt
    def add(self, other: Expression) -> Expression:
        other = parse_expr(other)
        if other.node_type == NodeType.CONSTANT:
            if other.is_zero:
                return self
            if self.operator.name == "add" and self.right.node_type == NodeType.CONSTANT:
                return Binop(self.left, "add", self.right + other)
        return Binop(self, "add", other)
    def mul(self, other: Expression) -> Expression:
        other = parse_expr(other)
        if other.node_type == NodeType.CONSTANT:
            if other.is_zero:
                return other
            if other.is_one:
                return self
            if self.operator.name == "mul" and self.right.node_type == NodeType.CONSTANT:
                return Binop(self.left, "mul", self.right * other)
        return Binop(self, "mul", other)
    def get_support_lib_function_name(self) -> str:
        if self.operator.name == "matmul":
            lt: typs.Tensor = self.left.resolved_type
            rt: typs.Tensor = self.right.resolved_type
            if lt is not None and rt is not None and lt.is_tensor and rt.is_tensor:
                return f"mul_{lt.name}_{rt.name}"
        return None
    def get_support_definitions(self, defs: compiler.SupportDefinitions):
        if self.operator.name == "matmul":
            lt: typs.Tensor = self.left.resolved_type
            rt: typs.Tensor = self.right.resolved_type
            if lt is not None and rt is not None and lt.is_tensor and rt.is_tensor:
                name = self.get_support_lib_function_name()
                if name is not None and defs.needs(name):
                    from alang.stmts import Set
                    from alang.exprs import parse_expr
                    ot = lt @ rt
                    f = funcs.Function(name, ot, ("a", lt), ("b", rt))
                    f.var("o", ot)
                    inner_count = rt.shape[0]
                    inner_add = None
                    o_index_expr = Index("o", ot.get_flat_index(["out_r", "out_c"]))
                    for inner_i in range(inner_count):
                        a_index = Index("a", lt.get_flat_index(("out_r", inner_i)))
                        b_index = Index("b", rt.get_flat_index((inner_i, "out_c")))
                        mul = a_index * b_index
                        if inner_add is None:
                            inner_add = mul
                        else:
                            inner_add = inner_add + mul
                    c_loop = stmts.Loop("out_c", ot.shape[1], Set(o_index_expr, inner_add))
                    f.loop("out_r", ot.shape[0], c_loop).ret("o")
                    defs.add(name, [f])
        return None
    
class Constant(Expression):
    value = NodeAttr()
    def __init__(self, value: object):
        super().__init__(NodeType.CONSTANT)
        self.value = value
    def _get_precedence(self):
        return 100
    @property
    def is_zero(self) -> bool:
        return (self.value == 0)
    @property
    def is_one(self) -> bool:
        return (self.value == 1)
    def resolve_type(self, diags: compiler.Diagnostics) -> typs.Type:
        v = self.value
        if v is None:
            return None
        if isinstance(v, int):
            return typs.int_type
        if isinstance(v, float):
            return typs.float_type
        return None
    def mul(self, other: Expression) -> Expression:
        if self.is_zero:
            return self
        other = parse_expr(other)
        if other.node_type == NodeType.CONSTANT:
            if other.is_zero:
                return other
            return Constant(self.value * other.value)
        return Binop(self, "mul", other)
    def add(self, other: Expression) -> Expression:
        other = parse_expr(other)
        if self.is_zero:
            return other
        if other.node_type == NodeType.CONSTANT:
            if other.is_zero:
                return self
            return Constant(self.value + other.value)
        return Binop(self, "add", other)
    def sub(self, other: Expression) -> Expression:
        other = parse_expr(other)
        if other.node_type == NodeType.CONSTANT:
            if other.is_zero:
                return self
            return Constant(self.value - other.value)
        return Binop(self, "sub", other)
    def div(self, other: Expression) -> Expression:
        if self.is_zero:
            return self
        other = parse_expr(other)
        if other.node_type == NodeType.CONSTANT:
            return Constant(self.value / other.value)
        return Binop(self, "div", other)

class Funcall(Expression):
    func = NodeLink()
    args = NodeLinks()
    def __init__(self, func: Expression, args: list[Expression] = []):
        super().__init__(NodeType.FUNCALL)
        self.func = parse_expr(func)
        for a in args:
            self.link(parse_expr(a), "args")
    def _get_precedence(self):
        return 100
    def resolve_type(self, diags: compiler.Diagnostics) -> typs.Type:
        f = self.func
        if f is None:
            return None
        ft = f.resolved_type
        if ft is None:
            return None
        return ft.return_type
    def write(self, writer: CodeWriter):
        f = self.func
        if f is None:
            return
        f.write(writer)
        writer.write("(")
        for i, arg in enumerate(self.args):
            if i > 0:
                writer.write(", ")
            arg.write(writer)
        writer.write(")")

class Index(Expression):
    base = NodeLink()
    ranges = NodeLinks()
    def __init__(self, base: Expression, *ranges: list[Expression]):
        super().__init__(NodeType.INDEX)
        self.base = parse_expr(base)
        for r in ranges:
            self.link(parse_expr(r), "ranges")
    def _get_precedence(self):
        return 100
    def resolve_type(self, diags: compiler.Diagnostics) -> typs.Type:
        bt: typs.Type = self.base.resolved_type
        if bt is None:
            return None
        if not bt.is_indexable:
            diags.error(f"Indexing not supported for type {bt}")
            return None
        return bt.element_type

def parse_expr(expr: object, context: Optional[Node] = None) -> Node:
    if expr is None:
        return None
    elif isinstance(expr, Node):
        return expr
    elif isinstance(expr, int):
        return Constant(expr)
    elif isinstance(expr, float):
        return Constant(expr)
    else:
        from alang.langs.a import a_lang
        return a_lang.parse_expr(expr)
