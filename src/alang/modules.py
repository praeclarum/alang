from typing import Optional
from nodes import Block, Node, NodeAttr, NodeLink, NodeLinks, NodeType
from funcs import Function

import typs

class Module(Block):
    name = NodeAttr()

    def __init__(self, name: str, can_define_statements: bool = False):
        super().__init__(NodeType.MODULE, can_define_types=True, can_define_functions=True, can_define_variables=True, can_define_statements=can_define_statements)
        if name is not None:
            self.name = name

    def resolve_type(self, diags: "compiler.Diagnostics") -> typs.Type: # type: ignore
        return typs.ModuleType(self.name)
