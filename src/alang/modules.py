from typing import Optional
from nodes import Block, Node, NodeAttr, NodeLink, NodeLinks, NodeType
from funcs import Function

class Module(Block):
    name = NodeAttr()

    def __init__(self, name: str = None):
        super().__init__(NodeType.MODULE, can_define_types=True, can_define_functions=True, can_define_variables=True)
        if name is not None:
            self.name = name

    def write_code(self, writer):
        writer.write_module(self)
