from typing import Optional
from langs.writer import CodeWriter
from nodes import Block, Node, NodeAttr, NodeLink, NodeLinks, NodeType
from stmts import Return
import typs

Code = str

class Function(Block):
    name = NodeAttr()
    parameters = NodeLinks()
    return_type = NodeLink()
    stage = NodeAttr()
    workgroup_size = NodeAttr()

    def __init__(self, name: str, return_type: Optional[typs.Type], *parameters: "Parameter"):
        super().__init__(NodeType.FUNCTION, can_define_types=False, can_define_functions=False, can_define_variables=True, can_define_statements=True)
        self.name = name
        self.return_type = typs.try_resolve_type(return_type, None)
        for p in parameters:
            if isinstance(p, Parameter):
                self.link(p, "parameters")
            else:
                self.param(p)

    def get_default_address_space(self) -> Optional[str]:
        return "function"

    def param(self, name: str, param_type: str = None, location: Optional[str] = None) -> "Function":
        if type(name) == tuple:
            name, param_type = name
        p = Parameter(name, parameter_type=typs.try_resolve_type(param_type, self), location=location)
        self.link(p, "parameters")
        return self
    
    def resolve_type(self, diags: "compiler.Diagnostics") -> typs.Type: # type: ignore
        if self.return_type is None:
            return None
        return_type = self.return_type.resolved_type
        if return_type is None:
            return None
        pts = []
        for p in self.parameters:
            pt = p.resolved_type
            if pt == None:
                return None
            pts.append(pt)
        return typs.FunctionType(return_type, pts)

class Parameter(Node):
    name = NodeAttr()
    parameter_type = NodeLink()
    location = NodeAttr()

    def __init__(self, name: str, parameter_type: "Type" = None, location: Optional[int] = None): # type: ignore
        super().__init__(NodeType.PARAMETER)
        self.name = name
        self.parameter_type = typs.try_resolve_type(parameter_type, None)
        self.location = location

    def resolve_type(self, diags: "compiler.Diagnostics") -> typs.Type: # type: ignore
        pt = self.parameter_type
        if pt is not None:
            return pt.resolved_type
