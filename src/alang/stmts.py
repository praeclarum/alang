from typing import Optional
from nodes import Expression, NodeAttr, NodeLink, NodeType, Statement

import langs

class Return(Statement):
    value = NodeLink()
    def __init__(self, value: Optional[Expression]):
        super().__init__(NodeType.RETURN)
        self.value = value
    def write_code(self, writer):
        writer.write_return(self)
