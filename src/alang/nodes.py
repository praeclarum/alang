
from typing import Callable


TypeRef = str

class Node:
    def __init__(self):
        pass

class NodeType:
    FUNCTION = 'function'

class NodeData:
    def __init__(self, type: NodeType):
        self.type = type
        self.attributes = {}
        self.children = []
        self.node = create_node_for_data(type, self)
    def set_type(self, new_type: NodeType) -> Node:
        self.type = new_type
        self.node = create_node_for_data(new_type, self)
        return self.node
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

class Function:
    def __init__(self, data: NodeData):
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

def create_node_for_data(type: NodeType, data: NodeData) -> Node:
    if type not in node_types:
        raise ValueError(f"Invalid node type: {type}")
    return node_types[type](data)
    
def create_node(type: NodeType) -> Node:
    return create_node_for_data(type, NodeData(type))

def define(name: str, *parameters: list[tuple[str, TypeRef]]) -> Function:
    n = create_node(NodeType.FUNCTION)
    n.set_name(name)
    for param in parameters:
        n.parameter(param)
    return n

if __name__ == "__main__":
    print(define("f", "x"))
