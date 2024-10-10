
import io
from typing import Callable, Optional, TypeVar, Union

TypeRef = str

class NodeType:
    FUNCTION = 'function'
    PARAMETER = 'parameter'
    TYPE = 'type'

next_node_id = 1

class Node:
    def __init__(self, type: NodeType):
        global next_node_id
        self.id = next_node_id
        next_node_id += 1
        self.type = type
        self.attributes: dict[str, "Attr"] = {}
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
    def __set__(self, obj: Node, value: Node):
        if value.type != self.child_node_type:
            raise ValueError(f"Expected child of type {self.child_node_type}, got {value.type}")
        num_children = len(obj.children)
        i = 0
        while i < len(obj.children):
            if obj.children[i].type == self.child_node_type:
                obj.children.pop(i)
            else:
                i += 1
        obj.children.insert(num_children, value)

class Function(Node):
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

class Parameter(Node):
    name = NodeAttr()
    parameter_type = NodeChild(NodeType.TYPE)

    def __init__(self, name: str = None, parameter_type: "Type" = None):
        super().__init__(NodeType.PARAMETER)
        if name is not None:
            self.name = name
        if parameter_type is not None:
            self.parameter_type = parameter_type

class Type(Node):
    name = NodeAttr()

    def __init__(self, name: str = None):
        super().__init__(NodeType.TYPE)
        if name is not None:
            self.name = name
