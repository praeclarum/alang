import io
from typing import Any, Callable, Optional, TypeVar, Union

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
    FIELD = 'field'
    FLOAT = 'float'
    FUNCTION = 'function'
    INTEGER = 'integer'
    MODULE = 'module'
    NAME = 'name'
    PARAMETER = 'parameter'
    RETURN = 'return'
    STRUCT = 'struct'
    VARIABLE = 'variable'
    VECTOR = 'vector'

class Node:
    def __init__(self, type: NodeType):
        self.node_type = type
        self.attributes: dict[str, "NodeAttr"] = {}
        self.links: list[tuple[str, "Node"]] = []
        self.last_backlink: Optional["Node"] = None
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
    def write(self, out, depth, rel):
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
                child.write(out, depth + 1, crel)
            out.write(f"{indent})\n")
        else:
            out.write("))\n")
    def __str__(self):
        out = io.StringIO()
        self.write(out, 0, None)
        return out.getvalue()
    def lookup_variable(self, name: str) -> Optional["Variable"]:
        p = self.last_backlink
        while p is not None:
            if isinstance(p, Node):
                return p.lookup_variable(name)
            p = p.parent
        return None
    def write_code(self, writer):
        raise NotImplementedError(f"Cannot write code for {self.node_type}")
    def get_code(self, language: Optional[Any] = None, options: Optional[CodeOptions] = None) -> str:
        language = langs.get_language(language)
        out = io.StringIO()
        with language.open_writer(out, options) as writer:
            self.write_code(writer)
        return out.getvalue()
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

class NodeRels:
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

class NodeRel:
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

class Expression(Node):
    def __init__(self, node_type: NodeType):
        super().__init__(node_type)
    def write_code(self, writer):
        writer.write_expr(self)

class Statement(Node):
    def __init__(self, node_type: NodeType):
        super().__init__(node_type)
    def write_code(self, writer):
        writer.write_stmt(self)

class Block(Node):
    types = NodeRels()
    variables = NodeRels()
    functions = NodeRels()
    def __init__(self, type: NodeType, can_define_types: bool, can_define_functions: bool, can_define_variables: bool):
        super().__init__(type)
        self.can_define_types = can_define_types
        self.can_define_functions = can_define_functions
        self.can_define_variables = can_define_variables
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
    def define(self, name: str, *parameters: list) -> "Function":
        if self.can_define_functions:
            from funcs import Function
            f = Function(name)
            for param in parameters:
                f.parameter(param)
            self.link(f, "functions")
            return f
        else:
            raise ValueError(f"Cannot define function in {self.node_type}")
    def struct(self, name: str, *fields: list) -> "Struct":
        if self.can_define_types:
            from typs import Struct
            s = Struct(name)
            for field in fields:
                s.field(*field)
            self.link(s, "types")
            return s
        else:
            raise ValueError(f"Cannot define struct in {self.node_type}")
    def array(self, element_type: str, length: Optional[int] = None) -> "Array":
        if self.can_define_types:
            from typs import Array
            a = Array(element_type, length)
            self.link(a, "types")
            return a
        else:
            raise ValueError(f"Cannot define array in {self.node_type}")

class Variable(Node):
    name = NodeAttr()
    variable_type = NodeRel()
    initial_value = NodeRel()

    def __init__(self, name: str, variable_type: Optional["Type"] = None, initial_value: Expression = None):
        super().__init__(NodeType.VARIABLE)
        self.name = name
        self.variable_type = variable_type
        self.initial_value = initial_value

    def write_code(self, writer):
        writer.write_variable(self)
