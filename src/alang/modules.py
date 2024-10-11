from typing import Optional
from nodes import Block, Node, NodeAttr, NodeChild, NodeChildren, NodeType
from funcs import Function

class Module(Block):
    name = NodeAttr()
    functions = NodeChildren(NodeType.FUNCTION)

    def __init__(self, name: str = None):
        super().__init__(NodeType.MODULE, can_define_functions=True, can_define_variables=True)
        if name is not None:
            self.name = name

    def define(self, name: str, *parameters: list) -> Function:
        f = Function(name)
        for param in parameters:
            f.parameter(param)
        self.append_child(f)
        return f
