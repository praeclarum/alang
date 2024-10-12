from typing import Optional
from nodes import Expression, NodeAttr, NodeChild, NodeType, Statement

import langs

class Return(Statement):
    value = NodeChild(NodeType.EXPRESSION)
    def __init__(self, value: Optional[Expression]):
        super().__init__()
        self.value = value
    def write_code(self, writer):
        writer.write_return(self)
