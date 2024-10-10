import io
from typing import Callable, Optional, TypeVar, Union

TypeRef = str

Code = str

class NodeType:
    EXPRESSION = 'expression'
    FUNCTION = 'function'
    MODULE = 'module'
    PARAMETER = 'parameter'
    STATEMENT = 'statement'
    TYPE = 'type'
    VARIABLE = 'variable'

class Node:
    def __init__(self, type: NodeType):
        self.type = type
        self.attributes: dict[str, "NodeAttr"] = {}
        self.children: list["Node"] = []
    def get_children_with_type(self, type: NodeType):
        return [child for child in self.children if child.type == type]
    def get_child_with_type(self, type: NodeType):
        return self.get_children_with_type(type)[0]
    def append_child(self, child: "Node"):
        self.children.append(child)
        return self
    def write(self, out, depth):
        if depth > 3:
            out.write("...")
            return
        indent = "    " * depth
        out.write(f"{indent}({self.type} (")
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
            if obj.children[i].type == self.child_node_type:
                obj.children.pop(i)
            else:
                i += 1
        for child in value:
            if child.type != self.child_node_type:
                raise ValueError(f"Expected child of type {self.child_node_type}, got {child.type}")
            obj.children.insert(num_children, child)
            num_children += 1

class NodeChild:
    def __init__(self, child_node_type: NodeType):
        self.child_node_type = child_node_type
    def __get__(self, obj: Node, objtype=None) -> list[Node]:
        return obj.get_child_with_type(self.child_node_type)
    def __set__(self, obj: Node, value: Optional[Node]):
        if value is not None and value.type != self.child_node_type:
            raise ValueError(f"Expected child of type {self.child_node_type}, got {value.type}")
        num_children = len(obj.children)
        i = 0
        while i < len(obj.children):
            if obj.children[i].type == self.child_node_type:
                obj.children.pop(i)
            else:
                i += 1
        if value is not None:
            obj.children.insert(num_children, value)

class Type(Node):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__(NodeType.TYPE)
        self.name = name

class ASTNode(Node):
    def __init__(self, type: NodeType):
        super().__init__(type)
    def lookup_variable(self, name: str) -> Optional["Variable"]:
        raise NotImplementedError

class Expression(ASTNode):
    def __init__(self):
        super().__init__(NodeType.EXPRESSION)

class Statement(ASTNode):
    def __init__(self):
        super().__init__(NodeType.STATEMENT)

import parser

class Block(ASTNode):
    def __init__(self, type: NodeType):
        super().__init__(type)
    def parse_expr(self, expr: Code) -> "Expression":
        return parser.parse_expr(expr)
    def set(self, lhs: Code, rhs: Code) -> "Block":
        raise NotImplementedError

class Scope(Block):
    variables = NodeChildren(NodeType.VARIABLE)
    def __init__(self, type: NodeType):
        super().__init__(type)
    def set(self, lhs: Code, rhs: Code) -> "Scope":
        lhs = self.parse_expr(lhs)
        rhs = self.parse_expr(rhs)
        v = self.lookup_variable(lhs)
        if v is None:
            v = Variable(lhs)
            self.append_child(v)
        return self
    def lookup_variable(self, name: str) -> Optional["Variable"]:
        raise NotImplementedError

class Variable(Node):
    name = NodeAttr()
    variable_type = NodeChild(NodeType.TYPE)
    initial_value = NodeChild(NodeType.EXPRESSION)

    def __init__(self, name: str, variable_type: Type = None, initial_value: Expression = None):
        super().__init__(NodeType.VARIABLE)
        self.name = name
        self.variable_type = variable_type
        self.initial_value = initial_value
