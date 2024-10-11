from typing import Optional
from alang.langs.writer import CodeWriter
from nodes import Block, Node, NodeAttr, NodeChild, NodeChildren, NodeType
from stmts import Return

Code = str

class Function(Block):
    name = NodeAttr()
    parameters = NodeChildren(NodeType.PARAMETER)
    returnType = NodeChild(NodeType.TYPE)

    def __init__(self, name: str = None):
        super().__init__(NodeType.FUNCTION, can_define_functions=False, can_define_variables=True)
        if name is not None:
            self.name = name

    def write_code(self, writer: CodeWriter):
        writer.write_function(self)

    def parameter(self, name: str, param_type: str = None) -> "Function":
        if type(name) == tuple:
            name, param_type = name
        p = Parameter(name, param_type)
        self.append_child(p)
        return self
    
    def ret(self, value: Optional[Code]) -> "Function":
        r = Return(self.parse_expr(value))
        return self

class Parameter(Node):
    name = NodeAttr()
    parameter_type = NodeChild(NodeType.TYPE)

    def __init__(self, name: str, parameter_type: "Type" = None):
        super().__init__(NodeType.PARAMETER)
        self.name = name
        self.parameter_type = parameter_type
