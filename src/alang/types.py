from typing import Optional
from nodes import ASTNode, Node, NodeChild, NodeChildren, NodeType, NodeAttr

class Type(ASTNode):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__(NodeType.TYPE)
        self.name = name

class Primitive(Type):
    def __init__(self, name):
        super().__init__(name)

class Field(Node):
    name = NodeAttr()
    type = NodeChild(NodeType.TYPE)
    def __init__(self, name: str, type: Type):
        super().__init__(NodeType.FIELD)
        self.name = name
        self.type = type

class Struct(Type):
    fields = NodeChildren(NodeType.FIELD)
    def __init__(self, name, fields: Optional[list[Field]] = None):
        super().__init__(name)
        if fields is not None:
            for field in fields:
                self.append_child(field)
