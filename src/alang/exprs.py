from alang.langs.writer import CodeWriter
from nodes import Expression, NodeAttr, NodeLink, NodeLinks, NodeType

import typs
import funcs

class Name(Expression):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__(NodeType.NAME)
        self.name = name
    
class Binop(Expression):
    left = NodeAttr()
    right = NodeAttr()
    operator = NodeAttr()
    def __init__(self, left: Expression, operator: str, right: Expression):
        super().__init__(NodeType.BINOP)
        self.left = left
        self.operator = operator
        self.right = right
    @staticmethod
    def get_binop(left: Expression, operator: str, right: Expression):
        if operator == "MatMul":
            f = funcs.get_matmul(left, right)
            if f is not None:
                return Funcall(f, [left, right])
        return Binop(left, operator, right)
    
class Funcall(Expression):
    func = NodeLink()
    args = NodeLinks()
    def __init__(self, func: Expression, args: list[Expression] = []):
        super().__init__(NodeType.FUNCALL)
        self.func = func
        for a in args:
            self.link(a, "args")
    def resolve_type(self, resolver):
        f = self.func
        if f is None:
            return None
        return f.resolve_type(resolver)
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
    def resolve_type(self, resolver):
        v = self.value
        if v is None:
            return None
        if isinstance(v, int):
            return typs.int_type
        if isinstance(v, float):
            return typs.float_type
        return None
