
from typing import Callable

TypeRef = str

class NodeType:
    FUNCTION = 'function'

next_node_id = 1

class NodeData:
    def __init__(self, type: NodeType):
        global next_node_id
        self.id = next_node_id
        next_node_id += 1
        self.type = type
        self.attributes = {}
        self.children = []
    def get_node(self) -> "Node":
        global node_types
        if self.type not in node_types:
            raise ValueError(f"Invalid node type: {type}")
        return node_types[self.type](self)
    def __getitem__(self, key):
        default = None
        if type(key) == tuple:
            default_ctor = key[1]
            key = key[0]
        if key in self.attributes:
            return self.attributes[key]
        if default_ctor is not None:
            default = default_ctor()
            self.attributes[key] = default
            return default
        return None
    def __setitem__(self, key: str, value):
        self.attributes[key] = value
    def __str__(self):
        return f"NodeData({self.type}, {self.attributes})"

class Node:
    def __init__(self, data: NodeData):
        self.data = data

class Function(Node):
    def __init__(self, data: NodeData):
        super().__init__(data)
        self.data = data

    @property
    def name(self):
        return self.data['name', ""]
    def set_name(self, name: str) -> "Function":
        self.data['name'] = name
        return self
    @property
    def parameters(self):
        return self.data['parameters', list]
    def parameter(self, name: str, param_type: TypeRef = None) -> "Function":
        if type(name) == tuple:
            name, param_type = name
        self.parameters.append((name, param_type))
        return self

    def __str__(self):
        return f"{self.name}({', '.join([f'{name}: {type_}' for name, type_ in self.parameters])})"
    def __repr__(self):
        return f"Function({self.name}, {self.parameters})"

node_types = {
    NodeType.FUNCTION: Function,
}

def create_node(type: NodeType) -> Node:
    return NodeData(type).get_node()

def define(name: str, *parameters: list[tuple[str, TypeRef]]) -> Function:
    n = create_node(NodeType.FUNCTION)
    n.set_name(name)
    for param in parameters:
        n.parameter(param)
    return n

if __name__ == "__main__":
    print(define("f", "x"))
