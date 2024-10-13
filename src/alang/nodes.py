import io
from typing import Any, Callable, Optional, TextIO, TypeVar, Union

import langs

TypeRef = str

Code = str
class CodeOptions:
    def __init__(self, standalone: bool = False, struct_annotations: bool = False) -> None:
        self.standalone = standalone
        self.struct_annotations = struct_annotations

class NodeType:
    ARRAY = 'array'
    BINOP = 'binop'
    CONSTANT = 'constant'
    EXPR_STMT = 'expr_stmt'
    FIELD = 'field'
    FLOAT = 'float'
    FOR = 'for'
    FUNCALL = 'funcall'
    FUNCTION = 'function'
    FUNCTION_TYPE = 'function_type'
    INTEGER = 'integer'
    MODULE = 'module'
    MODULE_TYPE = 'module_type'
    NAME = 'name'
    PARAMETER = 'parameter'
    RETURN = 'return'
    STRUCT = 'struct'
    TENSOR = 'tensor'
    TYPE_NAME = 'type_name'
    VARIABLE = 'variable'
    VOID = 'void'
    VECTOR = 'vector'

next_node_id = 1

class Node:
    def __init__(self, type: str):
        global next_node_id
        self.id = next_node_id
        next_node_id += 1
        self.node_type = type
        self.attributes: dict[str, "NodeAttr"] = {}
        self.links: list[tuple[str, "Node"]] = []
        self.last_backlink: Optional["Node"] = None
        self.resolved_type = None # all nodes get typed
        self.resolved_node = None # some nodes (name, type_name) get resolved to a node
    def append_backlink(self, backlink: "Node", rel: str):
        self.last_backlink = backlink
    def get_rels(self, rel: str) -> list["Node"]:
        return [child for (crel, child) in self.links if crel == rel]
    def get_rel(self, rel: str) -> Optional["Node"]:
        cs = self.get_rels(rel)
        return cs[0] if len(cs) > 0 else None
    def link(self, child: "Node", rel: str) -> "Node":
        self.links.append((rel, child))
        child.append_backlink(self, rel)
        return self
    def find_reachable_with_type(self, node_type: NodeType) -> list["Node"]:
        reachable = []
        for rel, link in self.links:
            if link.node_type == node_type:
                reachable.append(link)
            reachable.extend(link.find_reachable_with_type(node_type))
        return reachable
    def write_node(self, out, depth, rel):
        if depth > 5:
            out.write("...")
            return
        indent = "    " * depth
        out.write(f"{indent}({self.node_type} (")
        head = ""
        for k, a in self.attributes.items():
            out.write(f"{head}{a.name}={repr(getattr(self, a.private_name))}")
            head = " "
        if len(self.links) > 0:
            out.write(")\n")
            for crel, child in self.links:
                child.write_node(out, depth + 1, crel)
            out.write(f"{indent})\n")
        else:
            out.write("))\n")
    def __str__(self):
        out = io.StringIO()
        self.write_node(out, 0, None)
        return out.getvalue()
    def __repr__(self):
        return str(self)
    def lookup_variable(self, name: str) -> Optional["Variable"]:
        p = self.last_backlink
        while p is not None:
            if isinstance(p, Node):
                return p.lookup_variable(name)
            p = p.parent
        return None
    def resolve_type(self, diags) -> Optional["Type"]: # type: ignore
        raise NotImplementedError(f"resolve_type not implemented for {self.node_type}")
    def collect_support_definitions(self, grouped_support_definitions: dict[str, list["Node"]]):
        pass
    def write_code(self, out: Union[str, TextIO], language: Optional[Any] = None, options: Optional[CodeOptions] = None):
        from compiler import Compiler
        language = langs.get_language(language)
        compiler = Compiler(self)
        compiler.compile()
        with language.open_writer(out, options) as writer:
            for s in compiler.support_definitions:
                writer.write_support_node(s)
            writer.write_node(self)
            writer.write_diags(compiler.diags.messages)
    def get_code(self, language: Optional[Any] = None, options: Optional[CodeOptions] = None) -> str:
        out = io.StringIO()
        self.write_code(out, language, options)
        code = out.getvalue()
        return code
    @property
    def code(self) -> str:
        return self.get_code("a")
    @property
    def c_code(self) -> str:
        return self.get_code("c")
    @property
    def html_code(self) -> str:
        return self.get_code("html")
    @property
    def js_code(self) -> str:
        return self.get_code("js")
    @property
    def wgsl_code(self) -> str:
        return self.get_code("wgsl")
    
class NodeAttr:
    def __init__(self, default_value=None):
        self.default_value = default_value
    def __set_name__(self, owner: Node, name: str):
        self.name = name
        self.private_name = f"_{name}"
    def __get__(self, obj: Node, objtype=None):
        if hasattr(obj, self.private_name):
            return getattr(obj, self.private_name)
        return self.default_value
    def __set__(self, obj: Node, value):
        obj.attributes[self.name] = self
        setattr(obj, self.private_name, value)

class NodeLinks:
    def __init__(self):
        self.rel = None
    def __set_name__(self, owner: Node, name: str):
        self.rel = name
    def __get__(self, obj: Node, objtype=None) -> list[Node]:
        return obj.get_rels(self.rel)
    def __set__(self, obj: Node, value: list[Node]):
        i = 0
        while i < len(obj.links):
            if obj.links[i][0] == self.rel:
                ch = obj.links.pop(i)[1]
                ch.last_backlink = None
            else:
                i += 1
        for child in value:
            obj.link(child, self.rel)

class NodeLink:
    def __init__(self):
        self.rel = None
    def __set_name__(self, owner: Node, name: str):
        self.rel = name
    def __get__(self, obj: Node, objtype=None) -> list[Node]:
        return obj.get_rel(self.rel)
    def __set__(self, obj: Node, value: Optional[Node]):
        i = 0
        while i < len(obj.links):
            if obj.links[i][0] == self.rel:
                ch = obj.links.pop(i)[1]
                ch.last_backlink = None
            else:
                i += 1
        if value is not None:
            obj.link(value, self.rel)

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
        elif node.node_type == NodeType.FOR:
            return self.visit_for(node, parent, rel, acc)
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
    def visit_field(self, node: "Field", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_float(self, node: "Float", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_for(self, node: "For", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_funcall(self, node: "Funcall", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_function(self, node: "Function", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_integer(self, node: "Integer", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_module(self, node: "Module", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_name(self, node: "Name", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_parameter(self, node: "Parameter", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_return(self, node: "Return", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_struct(self, node: "Struct", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_tensor(self, node: "Tensor", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_vector(self, node: "Vector", parent: Node, rel: str, acc): # type: ignore
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

class Expression(Node):
    def __init__(self, node_type: NodeType):
        super().__init__(node_type)

class Statement(Node):
    def __init__(self, node_type: NodeType):
        super().__init__(node_type)

class Block(Node):
    types = NodeLinks()
    variables = NodeLinks()
    functions = NodeLinks()
    statements = NodeLinks()
    def __init__(self, type: NodeType, can_define_types: bool, can_define_functions: bool, can_define_variables: bool, can_define_statements: bool):
        super().__init__(type)
        self.can_define_types = can_define_types
        self.can_define_functions = can_define_functions
        self.can_define_variables = can_define_variables
        self.can_define_statements = can_define_statements
    def parse_expr(self, expr: Optional[Code]) -> Optional["Expression"]:
        return langs.get_language("a").parse_expr(expr)
    def append_any(self, child: Node):
        if child.node_type == NodeType.ARRAY:
            self.link(child, "types")
        elif child.node_type == NodeType.STRUCT:
            self.link(child, "types")
        elif child.node_type == NodeType.VARIABLE:
            self.link(child, "variables")
        elif child.node_type == NodeType.FUNCTION:
            self.link(child, "functions")
        else:
            raise ValueError(f"Cannot append {child.node_type} to {self.node_type}")
    def set(self, lhs: Code, rhs: Code) -> "Block":
        lhs = self.parse_expr(lhs)
        rhs = self.parse_expr(rhs)
        v = self.lookup_variable(lhs)
        if v is None:
            if self.can_define_variables:
                v = Variable(lhs)
                self.link(v, "variables")
            else:
                raise ValueError(f"Variable {lhs} not defined")
        else:
            raise ValueError(f"Variable {lhs} already defined")
        return self
    def define(self, name: str, *parameters: list) -> "Function": # type: ignore
        if self.can_define_functions:
            from funcs import Function
            f = Function(name, None, *parameters)
            self.link(f, "functions")
            return f
        else:
            raise ValueError(f"Cannot define function in {self.node_type}")
    def struct(self, name: str, *fields: list) -> "Struct": # type: ignore
        if self.can_define_types:
            from typs import Struct
            s = Struct(name)
            for field in fields:
                s.field(*field)
            self.link(s, "types")
            return s
        else:
            raise ValueError(f"Cannot define struct in {self.node_type}")
    def array(self, element_type: str, length: Optional[int] = None) -> "Array": # type: ignore
        if self.can_define_types:
            from typs import Array
            a = Array(element_type, length)
            self.link(a, "types")
            return a
        else:
            raise ValueError(f"Cannot define array in {self.node_type}")
    def call(self, func: str, *args: list) -> "Block":
        from exprs import Funcall
        from stmts import ExprStmt
        func = self.parse_expr(func)
        args = [self.parse_expr(x) for x in args]
        funcall = Funcall(func, args)
        stmt = ExprStmt(funcall)
        self.append_stmt(stmt)
        return self
    def forloop(self, init: str, cond: str, update: str) -> "For": # type: ignore
        from stmts import For
        init = self.parse_expr(init)
        cond = self.parse_expr(cond)
        update = self.parse_expr(update)
        f = For(init, cond, update)
        self.append_stmt(f)
        return self
    def ret(self, value: Optional[Code]) -> "Block":
        from stmts import Return
        r = Return(self.parse_expr(value))
        self.append_stmt(r)
        return self    
    def append_stmt(self, stmt):
        if not self.can_define_statements:
            raise ValueError(f"Cannot define return statements in {self.node_type}")
        self.link(stmt, "statements")

class Variable(Node):
    name = NodeAttr()
    variable_type = NodeLink()
    initial_value = NodeLink()

    def __init__(self, name: str, variable_type: Optional["Type"] = None, initial_value: Expression = None): # type: ignore
        super().__init__(NodeType.VARIABLE)
        self.name = name
        self.variable_type = variable_type
        self.initial_value = initial_value
