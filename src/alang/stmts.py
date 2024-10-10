from typing import Optional
from nodes import Expression, NodeAttr, Statement

class Return(Statement):
    value = NodeAttr()
    def __init__(self, value: Optional[Expression]):
        super().__init__()
        self.value = value
