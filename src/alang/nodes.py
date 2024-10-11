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
    EXPRESSION = 'expression'
    FIELD = 'field'
    FUNCTION = 'function'
    MODULE = 'module'
    PARAMETER = 'parameter'
    STATEMENT = 'statement'
    TYPE = 'type'
    VARIABLE = 'variable'

class Node:
    def __init__(self, type: NodeType):
        self.node_type = type
        self.attributes: dict[str, "NodeAttr"] = {}
        self.children: list["Node"] = []
        self.parent: Optional["Node"] = None
    def get_children_with_type(self, type: NodeType):
        return [child for child in self.children if child.node_type == type]
    def get_child_with_type(self, type: NodeType):
        return self.get_children_with_type(type)[0]
    def append_child(self, child: "Node"):
        self.children.append(child)
        child.parent = self
        return self
    def write(self, out, depth):
        if depth > 3:
            out.write("...")
            return
        indent = "    " * depth
        out.write(f"{indent}({self.node_type} (")
        head = ""
        for k, a in self.attributes.items():
            out.write(f"{head}{a.name}={repr(getattr(self, a.private_name))}")
            head = " "
        if len(self.children) > 0:
            out.write(")\n")
            for child in self.children:
                child.write(out, depth + 1)
            out.write(f"{indent})\n")
        else:
            out.write("))\n")
    def __str__(self):
        out = io.StringIO()
        self.write(out, 0)
        return out.getvalue()
    def lookup_variable(self, name: str) -> Optional["Variable"]:
        p = self.parent
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

class NodeChildren:
    def __init__(self, child_node_type: NodeType):
        self.child_node_type = child_node_type
    def __get__(self, obj: Node, objtype=None) -> list[Node]:
        return obj.get_children_with_type(self.child_node_type)
    def __set__(self, obj: Node, value: list[Node]):
        num_children = len(obj.children)
        i = 0
        while i < len(obj.children):
            if obj.children[i].node_type == self.child_node_type:
                obj.children.pop(i)
            else:
                i += 1
        for child in value:
            if child.node_type != self.child_node_type:
                raise ValueError(f"Expected child of type {self.child_node_type}, got {child.node_type}")
            obj.children.insert(num_children, child)
            num_children += 1

class NodeChild:
    def __init__(self, child_node_type: NodeType):
        self.child_node_type = child_node_type
    def __get__(self, obj: Node, objtype=None) -> list[Node]:
        return obj.get_child_with_type(self.child_node_type)
    def __set__(self, obj: Node, value: Optional[Node]):
        if value is not None and value.node_type != self.child_node_type:
            raise ValueError(f"Expected child of type {self.child_node_type}, got {value.node_type}")
        num_children = len(obj.children)
        i = 0
        while i < len(obj.children):
            if obj.children[i].node_type == self.child_node_type:
                obj.children.pop(i)
            else:
                i += 1
        if value is not None:
            obj.children.insert(num_children, value)

class Expression(Node):
    def __init__(self):
        super().__init__(NodeType.EXPRESSION)
    def write_code(self, writer):
        writer.write_expr(self)

class Statement(Node):
    def __init__(self):
        super().__init__(NodeType.STATEMENT)

class Block(Node):
    variables = NodeChildren(NodeType.VARIABLE)
    functions = NodeChildren(NodeType.FUNCTION)
    types = NodeChildren(NodeType.TYPE)
    def __init__(self, type: NodeType, can_define_types: bool, can_define_functions: bool, can_define_variables: bool):
        super().__init__(type)
        self.can_define_types = can_define_types
        self.can_define_functions = can_define_functions
        self.can_define_variables = can_define_variables
    def parse_expr(self, expr: Optional[Code]) -> Optional["Expression"]:
        return langs.get_language("a").parse_expr(expr)
    def set(self, lhs: Code, rhs: Code) -> "Block":
        lhs = self.parse_expr(lhs)
        rhs = self.parse_expr(rhs)
        v = self.lookup_variable(lhs)
        if v is None:
            if self.can_define_variables:
                v = Variable(lhs)
                self.append_child(v)
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
            self.append_child(f)
            return f
        else:
            raise ValueError(f"Cannot define function in {self.node_type}")
    def struct(self, name: str, *fields: list) -> "Struct":
        if self.can_define_types:
            from typs import Struct
            s = Struct(name)
            for field in fields:
                s.field(*field)
            self.append_child(s)
            return s
        else:
            raise ValueError(f"Cannot define struct in {self.node_type}")
    def array(self, element_type: str, length: Optional[int] = None) -> "Array":
        if self.can_define_types:
            from typs import Array
            a = Array(element_type, length)
            self.append_child(a)
            return a
        else:
            raise ValueError(f"Cannot define array in {self.node_type}")

class Variable(Node):
    name = NodeAttr()
    variable_type = NodeChild(NodeType.TYPE)
    initial_value = NodeChild(NodeType.EXPRESSION)

    def __init__(self, name: str, variable_type: Optional["Type"] = None, initial_value: Expression = None):
        super().__init__(NodeType.VARIABLE)
        self.name = name
        self.variable_type = variable_type
        self.initial_value = initial_value

    def write_code(self, writer):
        writer.write_variable(self)
