from alang.langs.writer import CodeWriter
from nodes import Expression, Node, NodeAttr, NodeLink, NodeLinks, NodeType

import compiler
import funcs
import typs

class Name(Expression):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__(NodeType.NAME)
        self.name = name
        self.resolved_node: Node = None
    def resolve_type(self):
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
    BinopOp("add", "+"),
    BinopOp("sub", "-"),
    BinopOp("mul", "*"),
    BinopOp("matmul", "@"),
    BinopOp("div", "/"),
    BinopOp("mod", "%"),
    BinopOp("eq", "=="),
    BinopOp("ne", "!="),
    BinopOp("lt", "<"),
    BinopOp("le", "<="),
    BinopOp("gt", ">"),
    BinopOp("ge", ">="),
    BinopOp("and", "&&"),
    BinopOp("or", "||"),
    BinopOp("xor", "^"),
    BinopOp("shl", "<<"),
    BinopOp("shr", ">>"),
    BinopOp("band", "&"),
    BinopOp("bor", "|"),    
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
        self.left = left
        self.right = right
    def resolve_type(self):
        lt: typs.Type = self.left.resolved_type
        rt: typs.Type = self.right.resolved_type
        if lt is None or rt is None:
            return None
        if not lt.is_algebraic or not rt.is_algebraic:
            return None
        opn = self.operator.name
        if opn == "matmul":
            if lt.is_tensor and rt.is_tensor:
                return lt @ rt
            else:
                return None
        elif opn in ["add", "sub", "mul", "div", "mod"]:
            if lt.is_floatish:
                return lt
            elif rt.is_floatish:
                return rt
            else:
                return lt
        elif opn in ["shl", "shr", "band", "bor"]:
            return lt
        else:
            raise NotImplementedError(f"resolve_type for op '{opn}' {self.operator.op} not implemented")
    
class Funcall(Expression):
    func = NodeLink()
    args = NodeLinks()
    def __init__(self, func: Expression, args: list[Expression] = []):
        super().__init__(NodeType.FUNCALL)
        self.func = func
        for a in args:
            self.link(a, "args")
    def resolve_type(self):
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

class Constant(Expression):
    value = NodeAttr()
    def __init__(self, value: object):
        super().__init__(NodeType.CONSTANT)
        self.value = value
    def resolve_type(self):
        v = self.value
        if v is None:
            return None
        if isinstance(v, int):
            return typs.int_type
        if isinstance(v, float):
            return typs.float_type
        return None
