import re
from typing import Optional
from nodes import Node, Node, NodeLink, NodeLinks, NodeType, NodeAttr

class Type(Node):
    name = NodeAttr()
    def __init__(self, name: str, node_type: NodeType):
        super().__init__(node_type)
        self.name = name
        self.is_scalar = False
        self.is_array = False
        self.is_vector = False
        self.is_struct = False
        self.is_tensor = False

    @property
    def layout(self) -> "TypeLayout":
        return self.get_layout(None)
    def get_layout(self, buffer_byte_size: Optional[int] = None) -> "TypeLayout":
        raise NotImplementedError(f"Type {self.name} does not have a layout")

    def write_code(self, writer):
        writer.write_type(self)

    def get_type_suffix(self) -> str:
        raise NotImplementedError()
    
class UnresolvedType(Type):
    def __init__(self, name: str):
        super().__init__(name, NodeType.UNRESOLVED_TYPE)
    def get_type_suffix(self) -> str:
        return "X"

class TypeLayout:
    def __init__(self):
        self.byte_size = 0
        self.align = 0

class ArrayLayout(TypeLayout):
    def __init__(self):
        super().__init__()
        self.element_stride = 0
        self.num_elements = 0

def get_array_layout(element_type: Type, length: Optional[int], buffer_byte_size: Optional[int] = None) -> ArrayLayout:
    e_layout = element_type.layout
    layout = ArrayLayout()
    layout.element_stride = round_up(e_layout.align, e_layout.byte_size)
    if length is None:
        if buffer_byte_size is None:
            print("Warning: Buffer size must be provided for runtime sized arrays")
            layout.num_elements = 0
        else:
            # If B is the effective buffer binding size for the binding on the
            # draw or dispatch command, the number of elements is:
            #   N_runtime = floor(B / element stride)
            layout.num_elements = buffer_byte_size // layout.element_stride
    else:
        layout.num_elements = length
    layout.byte_size = layout.element_stride * layout.num_elements
    layout.align = e_layout.align
    return layout

class Array(Type):
    element_type = NodeLink()
    length = NodeAttr()
    def __init__(self, element_type: Type, length: Optional[int]):
        element_type = try_resolve_type(element_type, self)
        super().__init__(f"{element_type.name}[{length}]", NodeType.ARRAY)
        self.element_type = element_type
        self.length = length
        self.nobuffer_layout = get_array_layout(element_type, length)
        self.is_array = True
    def get_layout(self, buffer_byte_size: Optional[int] = None) -> ArrayLayout:
        if buffer_byte_size is not None:
            return get_array_layout(self.element_type, self.length, buffer_byte_size)
        return self.nobuffer_layout
    @property
    def layout(self) -> ArrayLayout:
        return self.get_layout(None)
    @property
    def is_fixed_size(self) -> bool:
        return self.length is not None
    @property
    def is_runtime_sized(self) -> bool:
        return self.length is None
    def get_type_suffix(self) -> str:
        return "A"    

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
    
def get_int_layout(bits: int) -> TypeLayout:
    layout = TypeLayout()
    layout.byte_size = ((bits // 8 + 3) // 4) * 4
    layout.align = layout.byte_size
    return layout

class Integer(Type):
    bits = NodeAttr()
    signed = NodeAttr()
    def __init__(self, bits: int, signed: bool):
        super().__init__(get_int_name(bits, signed), NodeType.INTEGER)
        self.bits = bits
        self.signed = signed
        self.cached_layout = get_int_layout(bits)
        self.is_scalar = True
    def get_layout(self, buffer_byte_size: Optional[int] = None) -> TypeLayout:
        return self.cached_layout
    def get_type_suffix(self) -> str:
        return self.name[0]

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
    
def get_float_layout(bits: int) -> TypeLayout:
    layout = TypeLayout()
    layout.byte_size = ((bits // 8 + 3) // 4) * 4
    layout.align = layout.byte_size
    return layout

class Float(Type):
    bits = NodeAttr()
    def __init__(self, bits: int):
        super().__init__(get_float_name(bits), NodeType.FLOAT)
        self.bits = bits
        self.cached_layout = get_float_layout(bits)
        self.is_scalar = True
    def get_type_suffix(self) -> str:
        return self.name[0]
    def get_layout(self, buffer_byte_size: Optional[int] = None) -> TypeLayout:
        return self.cached_layout

half_type = Float(16)
float_type = Float(32)
double_type = Float(64)

class Field(Node):
    name = NodeAttr()
    field_type = NodeLink()
    def __init__(self, name: str, field_type: Type):
        super().__init__(NodeType.FIELD)
        self.name = name
        self.field_type = field_type

class FieldLayout(TypeLayout):
    def __init__(self):
        self.offset = 0
        self.num_elements = 0
    @property
    def triple(self) -> tuple[int, int, int]:
        """Returns a tuple of (offset, align, size)"""
        return (self.offset, self.align, self.byte_size)

class StructLayout(TypeLayout):
    def __init__(self):
        super().__init__()
        self.fields = []

def get_struct_layout(fields: list[Field], buffer_byte_size: Optional[int] = None) -> StructLayout:
    struct_layout = StructLayout()
    last_offset = 0
    last_size = 0
    max_field_align = 0
    if len(fields) == 0:
        return struct_layout
    for field_index, field in enumerate(fields):
        type_layout = field.field_type.layout
        offset = round_up(type_layout.align, last_offset + last_size)
        field_layout = FieldLayout()
        field_layout.offset = offset
        field_layout.num_elements = 1
        if buffer_byte_size is not None:
            remaining_bytes = buffer_byte_size - offset
            if remaining_bytes < 0:
                print(f"Warning: Buffer size too small for field {field.name}")
            else:
                type_layout = field.field_type.get_layout(remaining_bytes)
                if isinstance(type_layout, ArrayLayout):
                    field_layout.num_elements = type_layout.num_elements
        field_layout.byte_size = type_layout.byte_size
        field_layout.align = type_layout.align
        struct_layout.fields.append(field_layout)
        max_field_align = max(max_field_align, type_layout.align)
        last_offset = offset
        last_size = type_layout.byte_size
    struct_layout.align = max_field_align
    just_past_last_field = struct_layout.fields[-1].offset + struct_layout.fields[-1].byte_size
    struct_layout.byte_size = round_up(struct_layout.align, just_past_last_field)
    return struct_layout

def round_up(k: int, n: int) -> int:
    # roundUp(k, n) = ⌈n ÷ k⌉ × k
    return ((n + k - 1) // k) * k

class Struct(Type):
    fields = NodeLinks()
    def __init__(self, name, fields: Optional[list[Field]] = None):
        super().__init__(name, NodeType.STRUCT)
        if fields is not None:
            for field in fields:
                self.link(field, "fields")
        self.nobuffer_layout = None
        self.is_struct = True

    def get_layout(self, buffer_byte_size: Optional[int] = None) -> StructLayout:
        if buffer_byte_size is None:
            if self.nobuffer_layout is None:
                self.nobuffer_layout = get_struct_layout(self.fields)
            return self.nobuffer_layout
        else:
            return get_struct_layout(self.fields, buffer_byte_size)

    @property
    def layout(self) -> StructLayout:
        return self.get_layout(None)

    def field(self, name: str, type: Type) -> "Struct":
        f = Field(name, try_resolve_type(type, self))
        self.link(f, "fields")
        self.nobuffer_layout = None
        return self

    def write_code(self, writer):
        writer.write_struct(self)

def get_tensor_name(shape: tuple, element_type: Type):
    sn = "x".join([str(s) for s in shape])
    return f"{element_type.name}{sn}"

class Tensor(Type):
    element_type = NodeLink()
    shape = NodeAttr()
    def __init__(self, shape: tuple, element_type: Type):
        element_type = try_resolve_type(element_type, None)
        if element_type is None:
            raise ValueError(f"Cannot create tensor with unresolved element type: {element_type}")
        elif not element_type.is_scalar:
            raise ValueError(f"Cannot create tensor with non-scalar element type: {element_type}")
        super().__init__(get_tensor_name(shape, element_type), NodeType.TENSOR)
        self.element_type = element_type
        self.shape = shape
        num_elements = 1
        for s in shape:
            num_elements *= s
        self.num_elements = num_elements
        self.nobuffer_layout = get_array_layout(element_type, num_elements)
        self.is_tensor = True
    def get_layout(self, buffer_byte_size: Optional[int] = None) -> ArrayLayout:
        return self.nobuffer_layout
    def write_code(self, writer):
        writer.write_tensor(self)

def get_vector_name(element_type: Type, size: int) -> str:
    return f"vec{size}{element_type.get_type_suffix()}"

def get_vector_layout(element_type: Type, size: int) -> TypeLayout:
    e_layout: TypeLayout = element_type.layout
    layout = TypeLayout()
    if size == 2:
        layout.byte_size = e_layout.byte_size * 2
        layout.align = layout.byte_size
    elif size == 3:
        layout.byte_size = e_layout.byte_size * 3
        layout.align = e_layout.byte_size * 4
    elif size == 4:
        layout.byte_size = e_layout.byte_size * 4
        layout.align = layout.byte_size
    else:
        raise ValueError(f"Invalid vector size: {size}")
    return layout

class Vector(Type):
    element_type = NodeLink()
    size = NodeAttr()
    def __init__(self, element_type: Type, size: int):
        super().__init__(get_vector_name(element_type, size), NodeType.VECTOR)
        if size < 2 or size > 4:
            raise ValueError(f"Invalid vector size: {size}. Size must be 2, 3, or 4")
        self.element_type = element_type
        self.size = size
        self.nobuffer_layout = get_vector_layout(element_type, size)
        self.is_vector = True
    def get_layout(self, buffer_byte_size: Optional[int] = None) -> TypeLayout:
        return self.nobuffer_layout

vec2h_type = Vector(half_type, 2)
vec3h_type = Vector(half_type, 3)
vec4h_type = Vector(half_type, 4)

vec2f_type = Vector(float_type, 2)
vec3f_type = Vector(float_type, 3)
vec4f_type = Vector(float_type, 4)

vec2i_type = Vector(int_type, 2)
vec3i_type = Vector(int_type, 3)
vec4i_type = Vector(int_type, 4)

class Void(Type):
    """The void type used only for function return types"""
    def __init__(self):
        super().__init__("void", NodeType.VOID)
    def get_layout(self, buffer_byte_size: Optional[int] = None) -> TypeLayout:
        return TypeLayout()
    def write_code(self, writer):
        writer.write_void(self)

scalar_types = {
    sbyte_type.name: sbyte_type,
    byte_type.name: byte_type,
    short_type.name: short_type,
    ushort_type.name: ushort_type,
    int_type.name: int_type,
    uint_type.name: uint_type,
    long_type.name: long_type,
    ulong_type.name: ulong_type,

    half_type.name: half_type,
    float_type.name: float_type,
    double_type.name: double_type,
}

builtin_types = {
    vec2h_type.name: vec2h_type,
    vec3h_type.name: vec3h_type,
    vec4h_type.name: vec4h_type,
    vec2f_type.name: vec2f_type,
    vec3f_type.name: vec3f_type,
    vec4f_type.name: vec4f_type,
    vec2i_type.name: vec2i_type,
    vec3i_type.name: vec3i_type,
    vec4i_type.name: vec4i_type,
}
builtin_types.update(scalar_types)

def try_resolve_builtin_type(name: str) -> Optional[Type]:
    if name in builtin_types:
        return builtin_types[name]
    return None

def resolve_builtin_type(name: str) -> Type:
    bt = try_resolve_builtin_type(name)
    if bt is None:
        raise ValueError(f"Unknown builtin type: {name}")
    return bt

tensor_type_re = re.compile(r"^([a-z][a-z]+)(((\d+)x)+(\d+))$", 0)

def try_resolve_tensor_type(name: str) -> Optional[Type]:
    m = tensor_type_re.match(name)
    if m is None:
        return None
    element_type_name = m.group(1)
    element_type = try_resolve_builtin_type(element_type_name)
    if element_type is None:
        return None
    shape_str = m.group(2)
    shape = tuple([int(s) for s in shape_str.split("x")])
    return Tensor(shape, element_type)

def try_resolve_type(type, context: Optional[Node]) -> Type:
    if type is None:
        return None
    if isinstance(type, Type):
        return type
    if isinstance(type, str):
        bt = try_resolve_builtin_type(type)
        if bt is not None:
            return bt
        tt = try_resolve_tensor_type(type)
        if tt is not None:
            return tt
        # TODO: Implement lookup in context
    return UnresolvedType(type)

def tensor(shape: tuple, element_type: str):
    return Tensor(shape, try_resolve_type(element_type, None))

