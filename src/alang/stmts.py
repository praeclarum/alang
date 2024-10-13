from typing import Optional
from nodes import Expression, NodeAttr, NodeLink, NodeType, Statement

import typs

class ExprStmt(Statement):
    expression = NodeLink()
    def __init__(self, expression: Expression):
        super().__init__(NodeType.EXPR_STMT)
        self.expression = expression
    def resolve_type(self):
        return self.expression.resolved_type

class Return(Statement):
    value = NodeLink()
    def __init__(self, value: Optional[Expression]):
        super().__init__(NodeType.RETURN)
        self.value = value
    def resolve_type(self):
        if self.value is None:
            return typs.void_type
        return self.value.resolved_type
