from alang.languages.writer import CodeWriter
from nodes import Expression, NodeAttr

class Name(Expression):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    def write_code(self, writer: CodeWriter):
        writer.write_name(self)
    
class Binop(Expression):
    left = NodeAttr()
    right = NodeAttr()
    operator = NodeAttr()
    def __init__(self, left: Expression, operator: str, right: Expression):
        super().__init__()
        self.left = left
        self.operator = operator
        self.right = right
    def write_code(self, writer: CodeWriter):
        writer.write_binop(self)

class Constant(Expression):
    value = NodeAttr()
    def __init__(self, value: object):
        super().__init__()
        self.value = value
    def write_code(self, writer: CodeWriter):
        writer.write_constant(self)
