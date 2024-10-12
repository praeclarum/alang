from typing import Optional
from nodes import Expression, NodeAttr, NodeLink, NodeType, Statement

class ExprStmt(Statement):
    expression = NodeLink()
    def __init__(self, expression: Expression):
        super().__init__(NodeType.EXPR_STMT)
        self.expression = expression

class Return(Statement):
    value = NodeLink()
    def __init__(self, value: Optional[Expression]):
        super().__init__(NodeType.RETURN)
        self.value = value
