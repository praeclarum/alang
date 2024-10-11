from typing import Optional
from nodes import Node, Node, NodeChild, NodeChildren, NodeType, NodeAttr

class Type(Node):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__(NodeType.TYPE)
        self.name = name

    def write_code(self, writer):
        writer.write_type(self)

class Primitive(Type):
    def __init__(self, name):
        super().__init__(name)

def get_int_name(bits: int, signed: bool) -> str:
    if bits == 8:
        if signed:
            return "sbyte"
        else:
            return "byte"
    elif bits == 16:
        if signed:
            return "short"
        else:
            return "ushort"
    elif bits == 32:
        if signed:
            return "int"
        else:
            return "uint"
    elif bits == 64:
        if signed:
            return "long"
        else:
            return "ulong"
    else:
        raise ValueError(f"Invalid integer size: {bits}")

class Integer(Primitive):
    bits = NodeAttr()
    signed = NodeAttr()
    def __init__(self, bits: int, signed: bool):
        super().__init__(get_int_name(bits, signed))
        self.bits = bits
        self.signed = signed

sbyte_type = Integer(8, True)
byte_type = Integer(8, False)
short_type = Integer(16, True)
ushort_type = Integer(16, False)
int_type = Integer(32, True)
uint_type = Integer(32, False)
long_type = Integer(64, True)
ulong_type = Integer(64, False)

def get_float_name(bits: int) -> str:
    if bits == 16:
        return "half"
    elif bits == 32:
        return "float"
    elif bits == 64:
        return "double"
    else:
        raise ValueError(f"Invalid float size: {bits}")

class Float(Primitive):
    bits = NodeAttr()
    def __init__(self, bits: int):
        super().__init__(get_float_name(bits))
        self.bits = bits

float_type = Float(32)
double_type = Float(64)

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
    sbyte_type.name: sbyte_type,
    byte_type.name: byte_type,
    short_type.name: short_type,
    ushort_type.name: ushort_type,
    int_type.name: int_type,
    uint_type.name: uint_type,
    long_type.name: long_type,
    ulong_type.name: ulong_type,
    float_type.name: float_type,
    double_type.name: double_type
}
def resolve_builtin_type(name: str) -> Type:
    if name in builtin_types:
        return builtin_types[name]
    raise ValueError(f"Unknown type: {name}")
