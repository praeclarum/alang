from typing import Optional
from nodes import Code, Node, NodeAttr, NodeChild, NodeChildren, NodeType, Scope, Type

class Function(Scope):
    name = NodeAttr()
    parameters = NodeChildren(NodeType.PARAMETER)
    returnType = NodeChild(NodeType.TYPE)

    def __init__(self, name: str = None):
        super().__init__(NodeType.FUNCTION)
        if name is not None:
            self.name = name

    def parameter(self, name: str, param_type: str = None) -> "Function":
        if type(name) == tuple:
            name, param_type = name
        p = Parameter(name, param_type)
        self.append_child(p)
        return self


class Parameter(Node):
    name = NodeAttr()
    parameter_type = NodeChild(NodeType.TYPE)

    def __init__(self, name: str, parameter_type: Type = None):
        super().__init__(NodeType.PARAMETER)
        self.name = name
        self.parameter_type = parameter_type

