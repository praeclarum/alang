from typing import Optional
from nodes import BreadthFirstVisitor, CodeOptions, DepthFirstVisitor, Node, NodeType
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

class SupportDefinitions:
    def __init__(self):
        self.definitions: dict[str, list[Node]] = dict()
        self.num_changes = 0
    def add(self, group: str, defs: list[Node]):
        if group in self.definitions:
            return
        self.definitions[group] = defs
        self.num_changes += 1
    def get(self, name: str):
        return self.definitions.get(name)
    def needs(self, name: str):
        return name not in self.definitions

class CollectSupportDefinitions(DepthFirstVisitor):
    def __init__(self):
        self.defs = SupportDefinitions()
    @property
    def num_changes(self):
        return self.defs.num_changes
    @property
    def support_definitions(self):
        flattened = []
        for k, v in self.defs.definitions.items():
            flattened.extend(v)
        return flattened
    def run(self, node: Node):
        self.visit(node, None, None, None)
    def visit_node(self, node: Node, parent: Node, rel: str, acc):
        node.get_support_definitions(self.defs)
        super().visit_node(node, parent, rel, acc)

class Compiler:
    def __init__(self, ast: Node, options: CodeOptions):
        self.ast = ast
        self.options = options
        self.diags = Diagnostics()
        self.support_definitions = []
        self.entry_points = []

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
    
    def get_support_definitions(self):
        c = CollectSupportDefinitions()
        c.run(self.ast)
        return c.support_definitions
    
    def find_entry_points(self):
        import exprs, stmts, typs
        self.entry_points.clear()
        funcs: list[Function] = self.ast.find_reachable_with_type(NodeType.FUNCTION)
        for node in funcs:
            if node.stage is not None:
                self.entry_points.append((node, node.stage, None))
        if self.options.auto_entry_points and len(self.entry_points) == 0 and len(funcs) > 0:
            # Synthesize an entry point for the last function
            f = funcs[-1]
            ft = f.resolved_type
            if ft is None:
                self.diags.warning(f"Function {f.name}'s type could not be determined so it will not be used as an entry point", f)
            new_name = f.name + "_auto_compute"
            new_f = Function(new_name, void_type)
            new_f.stage = "compute"
            for pi, p in enumerate(f.parameters):
                new_f.param(p.name, ft.parameter_types[pi])
            # add outputs to ps
            call = exprs.Funcall(f, [p.name for p in f.parameters])
            # if not ft.return_type.is_void:
            #     new_f.param("_auto_out", ft.return_type).set("_auto_out", call)
            # else:
            new_f.stmt(stmts.ExprStmt(call))
            new_f.workgroup_size = 1
            self.entry_points.append((f, "compute", new_f))
    
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
        self.support_definitions = self.get_support_definitions()
        self.find_entry_points()
