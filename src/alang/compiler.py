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
        self.num_errors = 0
    def message(self, kind: str, message: str, node: Optional[Node] = None):
        m = DiagnosticMessage(kind, message, node)
        self.messages.append(m)
        if kind == DiagnosticKind.ERROR:
            self.num_errors += 1
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
        self.num_changes = 0
        self.num_need_info = 0
        self.num_errors = 0
    def resolve(self, node: Node) -> Type:
        if node.id in self.resolved_nodes:
            return self.resolved_nodes[node.id]
        if node.resolved_type is not None:
            self.resolved_nodes[node.id] = node.resolved_type
        if node.id in self.pending_nodes:
            self.diags.error("Circular reference detected", node)
            self.num_errors += 1
            return None
        self.pending_nodes.add(node.id)
        t = node.resolve_type(self)
        self.pending_nodes.remove(node.id)
        if t is None:
            self.num_need_info += 1
            return None
        self.num_changes += 1
        self.resolved_nodes[node.id] = t
        return t

class InferFunctionReturnType(DepthFirstVisitor):
    def __init__(self, diags: Diagnostics, type_resolver: TypeResolver):
        self.diags = diags
        self.type_resolver = type_resolver
        self.num_changes = 0
        self.num_need_info = 0
        self.num_errors = 0
    def visit_generic(self, node: Node, parent: Node, rel: str, cvals: list):
        return any(cvals)
    def set_return_type(self, node: Function, return_type: str):
        node.return_type = return_type
        self.num_changes += 1
    def visit_function(self, node: Function, parent: Node, rel: str, cvals: list):
        if node.return_type is not None:
            return
        return_values = [x.value for x in find_descendants_with_type(node, NodeType.RETURN)]
        if len(return_values) == 0 or all(x is None for x in return_values):
            # No return statements, or all return statements are empty, so return void
            self.set_return_type(node, void_type)
            return
        # See if any of them have resolved types
        maybe_resolved_types = [self.type_resolver.resolve(x) for x in return_values if x is not None]
        resolved_types = [x for x in maybe_resolved_types if x is not None]
        # Distinct them by name
        distinct_types = {}
        for t in resolved_types:
            distinct_types[t.name] = t
        if len(distinct_types) == 0:
            self.num_need_info += 1
            return
        if len(distinct_types) > 1:
            self.num_errors += 1
            self.diags.error(f"Multiple return types found: {distinct_types}", node)
        return_type = list(distinct_types.values())[0]
        self.set_return_type(node, return_type)

class Compiler:
    def __init__(self, ast: Node):
        self.ast = ast
        self.diags = Diagnostics()
        self.type_resolver = TypeResolver(self.diags)

    def infer_types(self) -> tuple[int, int, int]:
        visitor = InferFunctionReturnType(self.diags, self.type_resolver)
        visitor.visit(self.ast, None, None)
        return (visitor.num_changes, visitor.num_need_info, visitor.num_errors)
    
    def compile(self):
        should_iter = True
        max_iterations = 1_000
        iteration = 0
        while should_iter and iteration < max_iterations:
            infer_types_num_changes, infer_types_num_need_info, infer_types_num_errors = self.infer_types()
            should_iter = infer_types_num_changes > 0 #or infer_types_num_need_info > 0
            iteration += 1
        if iteration == max_iterations:
            self.diags.error("Max iterations reached")
