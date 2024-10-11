from typing import Optional
from nodes import ASTNode, Node, NodeChild, NodeChildren, NodeType, NodeAttr

class Type(ASTNode):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__(NodeType.TYPE)
        self.name = name

    def write_code(self, writer):
        writer.write_type(self)

class Primitive(Type):
    def __init__(self, name):
        super().__init__(name)

class Field(Node):
    name = NodeAttr()
    field_type = NodeChild(NodeType.TYPE)
    def __init__(self, name: str, field_type: Type):
        super().__init__(NodeType.FIELD)
        self.name = name
        self.field_type = field_type

class Struct(Type):
    fields = NodeChildren(NodeType.FIELD)
    def __init__(self, name, fields: Optional[list[Field]] = None):
        super().__init__(name)
        if fields is not None:
            for field in fields:
                self.append_child(field)

    def field(self, name: str, type: Type) -> "Struct":
        f = Field(name, resolve_builtin_type(type))
        self.append_child(f)
        return self

    def write_code(self, writer):
        writer.write_struct(self)

builtin_types = {
    "int32": Primitive("int32"),
}
def resolve_builtin_type(name: str) -> Type:
    if name in builtin_types:
        return builtin_types[name]
    raise ValueError(f"Unknown type: {name}")
