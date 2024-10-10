from typing import Optional
from nodes import Node, NodeAttr, NodeChild, NodeChildren, NodeType, Scope
from alang.funcs import Function

class Module(Scope):
    name = NodeAttr()
    functions = NodeChildren(NodeType.FUNCTION)

    def __init__(self, name: str = None):
        super().__init__(NodeType.MODULE)
        if name is not None:
            self.name = name

    def define(self, name: str, *parameters: list) -> Function:
        f = Function(name)
        for param in parameters:
            f.parameter(param)
        self.append_child(f)
        return f
