from typing import Optional
from nodes import BreadthFirstVisitor, DepthFirstVisitor, Node, NodeType
from typs import void_type
from funcs import Function

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
    def reset(self):
        self.messages = []
        self.num_errors = 0
    def message(self, kind: str, message: str, node: Optional[Node] = None):
        m = DiagnosticMessage(kind, message, node)
        self.messages.append(m)
        if kind == DiagnosticKind.ERROR:
            self.num_errors += 1
        # m.print()
    def error(self, message: str, node: Optional[Node] = None):
        self.message(DiagnosticKind.ERROR, message, node)
    def warning(self, message: str, node: Optional[Node] = None):
        self.message(DiagnosticKind.WARNING, message, node)

class TypeResolutionPass(DepthFirstVisitor):
    def __init__(self, diags: Diagnostics):
        self.diags = diags
        self.num_changes = 0
        self.num_need_info = 0
        self.num_errors = 0
    def run(self, node: Node):
        self.visit(node, None, None, None)
    def visit_node(self, node: Node, parent: Node, rel: str, acc):
        if node.resolved_type is not None:
            return
        t = node.resolve_type(self.diags)
        if t is None:
            self.num_need_info += 1
        else:
            node.resolved_type = t
            self.num_changes += 1
        return super().visit_node(node, parent, rel, acc)
    
class NameResolutionPass(BreadthFirstVisitor):
    def __init__(self, diags: Diagnostics):
        self.diags = diags
        self.num_changes = 0
        self.num_need_info = 0
        self.num_errors = 0
    def run(self, node: Node):
        self.visit(node, None, None, dict())
    def visit_name(self, node: Node, parent: Node, rel: str, env: dict): # type: ignore
        if node.resolved_node is not None:
            return env
        elif node.name in env:
            node.resolved_node = env[node.name]
            self.num_changes += 1
            return env
        else:
            self.diags.error(f"Name {node.name} not found", node)
            self.num_errors += 1
            return env
    def visit_function(self, node: Function, parent: Node, rel: str, env: dict):
        new_env = dict(env)
        for p in node.parameters:
            new_env[p.name] = p
        return new_env

class InferFunctionReturnTypePass(DepthFirstVisitor):
    def __init__(self, diags: Diagnostics):
        self.diags = diags
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
        return_values: list[Node] = [x.value for x in node.find_reachable_with_type(NodeType.RETURN)]
        if len(return_values) == 0 or all(x is None for x in return_values):
            # No return statements, or all return statements are empty, so return void
            self.set_return_type(node, void_type)
            return
        # See if any of them have resolved types
        maybe_resolved_types = [x.resolved_type for x in return_values if x is not None]
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

class CollectSupportDefinitions(DepthFirstVisitor):
    def __init__(self):
        self.grouped_support_definitions: dict[str, list[Node]] = dict()
    @property
    def support_definitions(self):
        flattened = []
        for k, v in self.grouped_support_definitions.items():
            flattened.extend(v)
        return flattened
    def run(self, node: Node):
        self.visit(node, None, None, None)
    def visit_node(self, node: Node, parent: Node, rel: str, acc):
        node.collect_support_definitions(self.grouped_support_definitions)
        super().visit_node(node, parent, rel, acc)

class Compiler:
    def __init__(self, ast: Node):
        self.ast = ast
        self.diags = Diagnostics()
        self.support_definitions = []

    def resolve_names(self):
        res_pass = NameResolutionPass(self.diags)
        res_pass.run(self.ast)
        return res_pass
    
    def resolve_types(self):
        res_pass = TypeResolutionPass(self.diags)
        res_pass.run(self.ast)
        return res_pass
    
    def infer_types(self):
        func_return_type_pass = InferFunctionReturnTypePass(self.diags)
        func_return_type_pass.run(self.ast)
        return func_return_type_pass
    
    def collect_support_definitions(self):
        c = CollectSupportDefinitions()
        c.run(self.ast)
        return c.support_definitions
    
    def compile(self):
        self.support_definitions.clear()
        should_iter = True
        max_iterations = 100
        iteration = 0
        while should_iter and iteration < max_iterations:
            self.diags.reset()
            resolve_name_info = self.resolve_names()
            resolve_types_info = self.resolve_types()
            infer_types_info = self.infer_types()
            should_iter = resolve_name_info.num_changes > 0 or resolve_types_info.num_changes > 0 or infer_types_info.num_changes > 0
            iteration += 1
        if iteration == max_iterations:
            self.diags.error("Max iterations reached")
        self.support_definitions = self.collect_support_definitions()
