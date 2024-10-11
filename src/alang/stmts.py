from typing import Optional
from alang.languages.writer import CodeWriter
from nodes import Expression, NodeAttr, Statement

class Return(Statement):
    value = NodeAttr()
    def __init__(self, value: Optional[Expression]):
        super().__init__()
        self.value = value
    def write_code(self, writer: CodeWriter):
        writer.write_return(self)
