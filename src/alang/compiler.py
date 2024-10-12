from nodes import Node, NodeType

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

    def visit_function(self, node: Node, parent: Node, rel: str, cvals: list):
        return None
    
class InferFunctionReturnType(DepthFirstVisitor):
    def visit_generic(self, node: Node, parent: Node, rel: str, cvals: list):
        return any(cvals)
    def visit_function(self, node: Node, parent: Node, rel: str, cvals: list):
        if node.return_type is not None:
            return any(cvals)
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
