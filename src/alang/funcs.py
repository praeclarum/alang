from typing import Optional
from alang.langs.writer import CodeWriter
from nodes import Block, Node, NodeAttr, NodeLink, NodeLinks, NodeType
from stmts import Return
import typs

Code = str

class Function(Block):
    name = NodeAttr()
    parameters = NodeLinks()
    returnType = NodeLink()

    def __init__(self, name: str = None):
        super().__init__(NodeType.FUNCTION, can_define_types=False, can_define_functions=False, can_define_variables=True)
        if name is not None:
            self.name = name

    def write_code(self, writer: CodeWriter):
        writer.write_function(self)

    def parameter(self, name: str, param_type: str = None) -> "Function":
        if type(name) == tuple:
            name, param_type = name
        p = Parameter(name, typs.try_resolve_type(param_type, self))
        self.link(p, "parameters")
        return self
    
    def ret(self, value: Optional[Code]) -> "Function":
        r = Return(self.parse_expr(value))
        self.link(r, "statements")
        return self

class Parameter(Node):
    name = NodeAttr()
    parameter_type = NodeLink()

    def __init__(self, name: str, parameter_type: "Type" = None): # type: ignore
        super().__init__(NodeType.PARAMETER)
        self.name = name
        self.parameter_type = typs.try_resolve_type(parameter_type, None)
