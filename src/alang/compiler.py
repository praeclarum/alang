from typing import Optional
from nodes import Node, NodeType
from funcs import Function
from typs import void_type, Type

class DiagnosticKind:
    ERROR = "error"
    WARNING = "warning"

class DiagnosticMessage:
    def __init__(self, kind: str, message: str, node: Optional[Node]):
        self.message = message
        self.node = node
        self.kind = kind
    def print(self):
        if self.node is not None:
            print(f"{self.kind.upper()}: {self.message} {self.node}")
        else:
            print(f"{self.kind.upper()}: {self.message}")

class Diagnostics:
    def __init__(self):
        self.messages: list[DiagnosticMessage] = []
    def message(self, kind: str, message: str, node: Optional[Node] = None):
        m = DiagnosticMessage(kind, message, node)
        self.messages.append(m)
        m.print()
    def error(self, message: str, node: Optional[Node] = None):
        self.message(DiagnosticKind.ERROR, message, node)
    def warning(self, message: str, node: Optional[Node] = None):
        self.message(DiagnosticKind.WARNING, message, node)

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
    
class TypeResolver:
    def __init__(self, diags: Diagnostics):
        self.diags = diags
        self.resolved_nodes: dict[int, Type] = dict()
        self.pending_nodes: set[int] = set() # prevent infinite recursion
    def resolve(self, node: Node) -> Type:
        if node.id in self.resolved_nodes:
            return self.resolved_nodes[node.id]
        if node.id in self.pending_nodes:
            self.diags.error("Circular reference detected", node)
            return None
        self.pending_nodes.add(node.id)
        print(f"Resolving {node}")
        t = node.resolve_type(self)
        self.pending_nodes.remove(node.id)
        if t is None:
            self.diags.error("Failed to resolve type", node)
            return None
        self.resolved_nodes[node.id] = t
        return t

class InferFunctionReturnType(DepthFirstVisitor):
    def __init__(self, diags: Diagnostics, type_resolver: TypeResolver):
        self.diags = diags
        self.type_resolver = type_resolver
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
        maybe_resolved_types = [self.type_resolver.resolve(x) for x in return_values if x is not None]
        resolved_types = [x for x in maybe_resolved_types if x is not None]
        # Distinct them by name
        distinct_types = {}
        for t in resolved_types:
            distinct_types[t.name] = t
        if len(distinct_types) == 0:
            return any(cvals)
        if len(distinct_types) > 1:
            self.diags.error(f"Multiple return types found: {distinct_types}", node)
        return_type = list(distinct_types.values())[0]
        self.set_return_type(node, return_type)
        return True

class Compiler:
    def __init__(self, ast: Node):
        self.ast = ast
        self.diags = Diagnostics()
        self.type_resolver = TypeResolver(self.diags)

    def infer_types(self) -> bool:
        """Performs one step of type inference on the AST.
        For full inference, keep running this method until it returns False.
        """
        visitor = InferFunctionReturnType(self.diags, self.type_resolver)
        return visitor.visit(self.ast, None, None)
    
    def compile(self):
        self.infer_types()
