from nodes import Node, NodeType
from funcs import Function
from typs import void_type

class DepthFirstVisitor:
    def visit(self, node: Node, parent: Node, rel: str):
        cvals = []
        for crel, child in node.links:
            cvals.append(self.visit(child, node, crel))
        if node.node_type == NodeType.FUNCTION:
            return self.visit_function(node, parent, rel, cvals)
        else:
            return self.visit_generic(node, parent, rel, cvals)

    def visit_generic(self, node: Node, parent: Node, rel: str, cvals: list):
        return None

    def visit_function(self, node: Function, parent: Node, rel: str, cvals: list):
        return None
    
def find_descendants_with_type(node: Node, node_type: NodeType) -> list[Node]:
    descendants = []
    for rel, child in node.links:
        if child.node_type == node_type:
            descendants.append(child)
        descendants.extend(find_descendants_with_type(child, node_type))
    return descendants
    
class InferFunctionReturnType(DepthFirstVisitor):
    def visit_generic(self, node: Node, parent: Node, rel: str, cvals: list):
        return any(cvals)
    def set_return_type(self, node: Function, return_type: str):
        node.return_type = return_type
    def visit_function(self, node: Function, parent: Node, rel: str, cvals: list):
        if node.return_type is not None:
            return any(cvals)
        return_values = [x.value for x in find_descendants_with_type(node, NodeType.RETURN)]
        if len(return_values) == 0:
            # No return statements, so must be void
            self.set_return_type(node, void_type)
            return True
        # See if any of them have resolved types
        resolved_types = [x.resolved_type for x in return_values if x is not None and x.resolved_type is not None]
        # Distinct them by name
        distinct_types = {}
        for t in resolved_types:
            distinct_types[t.name] = t
        raise NotImplementedError("Cannot infer return type of function")

class Compiler:
    def __init__(self, ast: Node):
        self.ast = ast

    def infer_types(self) -> bool:
        """Performs one step of type inference on the AST.
        For full inference, keep running this method until it returns False.
        """
        visitor = InferFunctionReturnType()
        return visitor.visit(self.ast, None, None)
