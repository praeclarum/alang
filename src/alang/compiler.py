from typing import Optional
from nodes import Node, NodeType
from typs import Field, Integer, Struct, Tensor, Vector, void_type, Type
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
    def reset(self):
        self.messages = []
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
        elif node.node_type == NodeType.CONSTANT:
            return self.visit_constant(node, parent, rel, acc)
        elif node.node_type == NodeType.EXPR_STMT:
            return self.visit_expr_stmt(node, parent, rel, acc)
        elif node.node_type == NodeType.FIELD:
            return self.visit_field(node, parent, rel, acc)
        elif node.node_type == NodeType.FLOAT:
            return self.visit_float(node, parent, rel, acc)
        elif node.node_type == NodeType.FUNCALL:
            return self.visit_funcall(node, parent, rel, acc)
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
        elif node.node_type == NodeType.STRUCT:
            return self.visit_struct(node, parent, rel, acc)
        elif node.node_type == NodeType.TENSOR:
            return self.visit_tensor(node, parent, rel, acc)
        elif node.node_type == NodeType.VECTOR:
            return self.visit_vector(node, parent, rel, acc)
        elif node.node_type == NodeType.VOID:
            return self.visit_void(node, parent, rel, acc)
        else:
            missing_code = f"elif node.node_type == NodeType.{node.node_type.upper()}:\n    return self.visit_{node.node_type.lower()}(node, parent, rel, acc)"
            print(missing_code)
            return acc
    def visit_binop(self, node: "Binop", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_constant(self, node: "Constant", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_expr_stmt(self, node: "ExprStmt", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_funcall(self, node: "Funcall", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_field(self, node: Field, parent: Node, rel: str, acc):
        return acc
    def visit_float(self, node: "Float", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_function(self, node: Function, parent: Node, rel: str, acc):
        return acc
    def visit_integer(self, node: Integer, parent: Node, rel: str, acc):
        return acc
    def visit_module(self, node: "Module", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_name(self, node: "Name", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_parameter(self, node: Parameter, parent: Node, rel: str, acc):
        return acc
    def visit_return(self, node: "Return", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_struct(self, node: Struct, parent: Node, rel: str, acc):
        return acc
    def visit_tensor(self, node: Tensor, parent: Node, rel: str, acc):
        return acc
    def visit_vector(self, node: Vector, parent: Node, rel: str, acc):
        return acc
    def visit_void(self, node: Node, parent: Node, rel: str, acc):
        return acc
    
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
        return_values: list[Node] = [x.value for x in find_descendants_with_type(node, NodeType.RETURN)]
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

class Compiler:
    def __init__(self, ast: Node):
        self.ast = ast
        self.diags = Diagnostics()

    def resolve_names(self) -> tuple[int, int, int]:
        res_pass = NameResolutionPass(self.diags)
        res_pass.run(self.ast)
        return res_pass
    
    def resolve_types(self) -> tuple[int, int, int]:
        res_pass = TypeResolutionPass(self.diags)
        res_pass.run(self.ast)
        return res_pass
    
    def infer_types(self) -> tuple[int, int, int]:
        func_return_type_pass = InferFunctionReturnTypePass(self.diags)
        func_return_type_pass.run(self.ast)
        return func_return_type_pass
    
    def compile(self):
        should_iter = True
        max_iterations = 1_000
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
