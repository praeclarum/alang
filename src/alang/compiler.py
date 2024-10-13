from typing import Optional
from nodes import Node, NodeType
from typs import Integer, Tensor, void_type, Type
from funcs import Function, Parameter

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

class Visitor:
    def visit(self, node: Node, parent: Node, rel: str, acc):
        raise NotImplementedError()
    def visit_node(self, node: Node, parent: Node, rel: str, acc):
        if node.node_type == NodeType.BINOP:
            return self.visit_binop(node, parent, rel, acc)
        elif node.node_type == NodeType.FUNCTION:
            return self.visit_function(node, parent, rel, acc)
        elif node.node_type == NodeType.INTEGER:
            return self.visit_integer(node, parent, rel, acc)
        elif node.node_type == NodeType.MODULE:
            return self.visit_module(node, parent, rel, acc)
        elif node.node_type == NodeType.NAME:
            return self.visit_name(node, parent, rel, acc)
        elif node.node_type == NodeType.PARAMETER:
            return self.visit_parameter(node, parent, rel, acc)
        elif node.node_type == NodeType.RETURN:
            return self.visit_return(node, parent, rel, acc)
        elif node.node_type == NodeType.TENSOR:
            return self.visit_tensor(node, parent, rel, acc)
        else:
            missing_code = f"elif node.node_type == NodeType.{node.node_type.upper()}:\n    return self.visit_{node.node_type.lower()}(node, parent, rel, acc)"
            print(missing_code)
            return None
    def visit_binop(self, node: "Binop", parent: Node, rel: str, acc): # type: ignore
        return None
    def visit_function(self, node: Function, parent: Node, rel: str, acc):
        return None
    def visit_integer(self, node: Integer, parent: Node, rel: str, acc):
        return None
    def visit_module(self, node: "Module", parent: Node, rel: str, acc): # type: ignore
        return None
    def visit_name(self, node: "Name", parent: Node, rel: str, acc): # type: ignore
        return None
    def visit_parameter(self, node: Parameter, parent: Node, rel: str, acc):
        return None
    def visit_return(self, node: Node, parent: Node, rel: str, acc):
        return None
    def visit_tensor(self, node: Tensor, parent: Node, rel: str, acc):
        return None
    
class DepthFirstVisitor(Visitor):
    def visit(self, node: Node, parent: Node, rel: str, acc):
        sacc = []
        for crel, child in node.links:
            sacc.append(self.visit(child, node, crel, acc))
        return self.visit_node(node, parent, rel, sacc)

class BreadthFirstVisitor(Visitor):
    def visit(self, node: Node, parent: Node, rel: str, acc):
        cacc = self.visit_node(node, parent, rel, acc)
        for crel, child in node.links:
            self.visit(child, node, crel, cacc)

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
            self.diags.error("Circular type reference detected", node)
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
    
class NameResolver(BreadthFirstVisitor):
    def __init__(self, diags: Diagnostics):
        self.diags = diags
        self.num_changes = 0
        self.num_need_info = 0
        self.num_errors = 0
    def run(self, node: Node):
        self.visit(node, None, None, [dict()])
    def visit_name(self, node: "Name", parent: Node, rel: str, acc): # type: ignore
        return super().visit_name(node, parent, rel, acc)
    def visit_function(self, node: Function, parent: Node, rel: str, acc):
        return super().visit_function(node, parent, rel, acc)

class InferFunctionReturnType(DepthFirstVisitor):
    def __init__(self, diags: Diagnostics, type_resolver: TypeResolver):
        self.diags = diags
        self.type_resolver = type_resolver
        self.num_changes = 0
        self.num_need_info = 0
        self.num_errors = 0
    def run(self, node: Node):
        self.visit(node, None, None, None)
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
        infer_return_type = InferFunctionReturnType(self.diags, self.type_resolver)
        infer_return_type.run(self.ast)
        return (infer_return_type.num_changes, infer_return_type.num_need_info, infer_return_type.num_errors)
    
    def resolve_names(self) -> tuple[int, int, int]:
        name_resolver = NameResolver(self.diags)
        name_resolver.run(self.ast)
        return (name_resolver.num_changes, name_resolver.num_need_info, name_resolver.num_errors)
    
    def compile(self):
        should_iter = True
        should_infer_types = True
        should_resolve_names = True
        max_iterations = 1_000
        iteration = 0
        while should_iter and iteration < max_iterations:
            should_iter = False
            if should_infer_types:
                infer_types_num_changes, infer_types_num_need_info, infer_types_num_errors = self.infer_types()
                should_infer_types = infer_types_num_changes > 0
                should_iter = should_iter or should_infer_types
            if should_resolve_names:
                resolve_names_num_changes, resolve_names_num_need_info, resolve_names_num_errors = self.resolve_names()
                should_resolve_names = resolve_names_num_changes > 0
                should_iter = should_iter or should_resolve_names
            iteration += 1
        if iteration == max_iterations:
            self.diags.error("Max iterations reached")
