import struct
from io import BytesIO
from typing import BinaryIO, Optional
from alang.typs import Array, Float, Integer, Scalar, Struct, Tensor, Type, Vector

class Value:
    def __init__(self, type: Type):
        self.type = type
    def get_python_value(self):
        raise NotImplementedError()
    def write(self, out: BinaryIO, buffer_byte_size: Optional[int] = None):
        raise NotImplementedError()
    def serialize(self, buffer_byte_size: Optional[int] = None) -> bytes:
        out = BytesIO()
        self.write(out, buffer_byte_size=buffer_byte_size)
        return out.getvalue()

class ScalarValue(Value):
    def __init__(self, type: Scalar, value):
        super().__init__(type)
        self.value = value
    def get_python_value(self):
        return self.value
    
class FloatValue(ScalarValue):
    def __init__(self, type: Float, value):
        super().__init__(type, value)
        self.type: Float
    def write(self, out: BinaryIO, buffer_byte_size: Optional[int] = None):
        if self.type.bits == 16:
            out.write(struct.pack("<e", self.value))
        elif self.type.bits == 32:
            out.write(struct.pack("<f", self.value))
        elif self.type.bits == 64:
            out.write(struct.pack("<d", self.value))
        else:
            raise ValueError(f"Invalid float type: {self.type.name}")

class IntegerValue(ScalarValue):
    def __init__(self, type: Integer, value):
        super().__init__(type, value)
        self.type: Integer
    def write(self, out: BinaryIO, buffer_byte_size: Optional[int] = None):
        out.write(self.value.to_bytes(self.type.bits // 8, "little"))

class StructValue(Value):
    def __init__(self, type: Struct, **kwargs):
        super().__init__(type)
        self.type: Struct
        self.values: dict[str, Value] = {}
        for f in type.fields:
            if f.name in kwargs:
                self.set_field_value(f.name, kwargs[f.name])
            else:
                ft = (f.resolved_type or f.field_type.resolved_type) or f.field_type
                self.values[f.name] = ft.create()

    def get_python_value(self):
        return self

    def find_field(self, name: str):
        for f in self.type.fields:
            if f.name == name:
                return f
        return None
    
    def set_field_value(self, name: str, value):
        if value is None:
            raise ValueError(f"Field value cannot be None: {name}")
        f = self.find_field(name)
        if f is None:
            raise AttributeError(f"Field not found: {name}")
        if not isinstance(value, Value):
            ft = (f.resolved_type or f.field_type.resolved_type) or f.field_type
            if ft is None:
                raise ValueError(f"Field type not resolved: {name}")
            value = ft.create(value)
        else:
            if value.type.type != ft:
                raise ValueError(f"Field value type mismatch: {name}")
        self.values[name] = value

    def __getattr__(self, name: str):
        f = self.find_field(name)
        if f is None:
            raise AttributeError(f"Field not found: {name}")
        return self.values[name].get_python_value()
    
    def __setattr__(self, name: str, value) -> None:
        if name == "type" or name == "values":
            super().__setattr__(name, value)
        else:
            self.set_field_value(name, value)

    def write(self, out: BinaryIO, buffer_byte_size: Optional[int] = None):
        st = self.type.resolved_type or self.type
        sl = st.get_layout(buffer_byte_size=buffer_byte_size)
        fls = sl.fields
        offset = 0
        for fi, f in enumerate(st.fields):
            fl = fls[fi]
            if offset != fl.offset:
                raise ValueError(f"Field offset mismatch: {f.name}. At={offset}, Expected={fl.offset}")
            self.values[f.name].write(out)
            offset += fls[fi].byte_size
            if fi < len(st.fields) - 1:
                num_padding = fls[fi + 1].offset - offset
                if num_padding > 0:
                    out.write(b"\x00" * num_padding)
                    offset += num_padding
    
class TensorValue(Value):
    def __init__(self, type: Tensor, value):
        super().__init__(type)
        self.type: Tensor
        self.value = value

class VectorValue(Value):
    def __init__(self, type: Vector, x=None, y=None, z=None, w=None):
        super().__init__(type)
        self.type: Vector
        zero = 0.0 if type.element_type.is_float else 0
        self.x = x or zero
        self.y = y or zero
        if type.num_elements >= 3:
            self.z = z or zero
        if type.num_elements >= 4:
            self.w = w or zero

    def get_python_value(self):
        return [self.x, self.y, self.z, self.w]
    
    def write(self, out: BinaryIO, buffer_byte_size: Optional[int] = None):
        for v in [self.x, self.y, self.z, self.w]:
            if isinstance(v, Value):
                v.write(out)
            else:
                if self.type.element_type.is_float:
                    FloatValue(self.type.element_type, v).write(out)
                else:
                    IntegerValue(self.type.element_type, v).write(out)
