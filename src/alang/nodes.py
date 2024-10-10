
from typing import Callable, Optional, TypeVar, Union

TypeRef = str

class NodeType:
    FUNCTION = 'function'

next_node_id = 1

class NodeData:
    def __init__(self, type: NodeType, node: Optional["Node"] = None):
        global next_node_id
        self.id = next_node_id
        next_node_id += 1
        self.type = type
        self.attributes = {}
        self.children = []
        self._node = node
    @property
    def node(self) -> "Node":
        global node_types
        if self._node is None:
            if self.type not in node_types:
                raise ValueError(f"Invalid node type: {type}")
            self._node = node_types[self.type](self)
        return self._node
    def astype(self, type: NodeType) -> "NodeData":
        if type == self.type:
            return self
        print(f"??? {self}: {self.type} -> {type}")
        self.type = type
        self._node = None
        return self
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
        return f"({self.type} {self.attributes})"

class Node:
    def __init__(self, type: NodeType, data: Optional[NodeData] = None):
        self.data = data.astype(type) if data is not None else NodeData(type, self)
    def __str__(self):
        return str(self.data)

class Function(Node):
    def __init__(self, data: Optional[NodeData] = None):
        super().__init__(NodeType.FUNCTION, data)

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

node_types = {
    NodeType.FUNCTION: Function,
}
