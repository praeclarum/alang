
import io
from typing import Callable, Optional, TypeVar, Union

TypeRef = str
Code = str

class NodeType:
    EXPRESSION = 'expression'
    FUNCTION = 'function'
    MODULE = 'module'
    PARAMETER = 'parameter'
    TYPE = 'type'
    VARIABLE = 'variable'

next_node_id = 1

class Node:
    def __init__(self, type: NodeType):
        global next_node_id
        self.id = next_node_id
        next_node_id += 1
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
    def lookup_variable(self, lhs: "Node" | str) -> Optional["Variable"]:
        if expr.type == NodeType.VARIABLE:
            return expr
        return None

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

class Expression(Node):
    def __init__(self):
        super().__init__(NodeType.EXPRESSION)

class Block(Node):
    def __init__(self, type: NodeType):
        super().__init__(type)
    def set(self, lhs: Code, rhs: Code) -> "Block":
        raise NotImplementedError
    def parse_expr(self, expr: Code) -> tuple[Node, Node]:
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
    def lookup_variable(self, lhs: "Node" | str) -> Optional["Variable"]:
        return super().lookup_variable(lhs)

class Function(Scope):
    name = NodeAttr()
    parameters = NodeChildren(NodeType.PARAMETER)
    returnType = NodeChild(NodeType.TYPE)

    def __init__(self, name: str = None):
        super().__init__(NodeType.FUNCTION)
        if name is not None:
            self.name = name

    def parameter(self, name: str, param_type: TypeRef = None) -> "Function":
        if type(name) == tuple:
            name, param_type = name
        p = Parameter(name, param_type)
        self.append_child(p)
        return self
    
class Module(Scope):
    name = NodeAttr()
    functions = NodeChildren(NodeType.FUNCTION)

    def __init__(self, name: str = None):
        super().__init__(NodeType.MODULE)
        if name is not None:
            self.name = name

    def define(self, name: str, *parameters: list[tuple[str, TypeRef]]) -> Function:
        f = Function(name)
        for param in parameters:
            f.parameter(param)
        self.append_child(f)
        return f

class Parameter(Node):
    name = NodeAttr()
    parameter_type = NodeChild(NodeType.TYPE)

    def __init__(self, name: str, parameter_type: "Type" = None):
        super().__init__(NodeType.PARAMETER)
        self.name = name
        self.parameter_type = parameter_type

class Variable(Node):
    name = NodeAttr()
    variable_type = NodeChild(NodeType.TYPE)
    initial_value = NodeChild(NodeType.EXPRESSION)

    def __init__(self, name: str, variable_type: Type = None, initial_value: Expression = None):
        super().__init__(NodeType.VARIABLE)
        self.name = name
        self.variable_type = variable_type
        self.initial_value = initial_value

