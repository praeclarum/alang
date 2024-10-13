from typing import Optional
from nodes import Block, Expression, NodeAttr, NodeLink, NodeType, Statement

import typs

class ExprStmt(Statement):
    expression = NodeLink()
    def __init__(self, expression: Expression):
        super().__init__(NodeType.EXPR_STMT)
        self.expression = expression
    def resolve_type(self, diags: "compiler.Diagnostics") -> typs.Type: # type: ignore
        return self.expression.resolved_type
    
class Loop(Block):
    var = NodeAttr()
    count = NodeLink()
    def __init__(self, var: str, count: Optional[Expression], *statements: list[Statement]):
        super().__init__(NodeType.LOOP, can_define_types=False, can_define_functions=False, can_define_variables=False, can_define_statements=True)
        self.var = var
        self.count = count
        self.statements = statements
    def resolve_type(self, diags: "compiler.Diagnostics") -> typs.Type: # type: ignore
        return typs.void_type

class Return(Statement):
    value = NodeLink()
    def __init__(self, value: Optional[Expression]):
        super().__init__(NodeType.RETURN)
        self.value = value
    def resolve_type(self, diags: "compiler.Diagnostics") -> typs.Type: # type: ignore
        if self.value is None:
            return typs.void_type
        return self.value.resolved_type
