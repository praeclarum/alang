
from typing import BinaryIO
from alang.typs import Array, Float, Integer, Scalar, Struct, Tensor, Type, Vector

class Value:
    def __init__(self, type: Type):
        self.type = type
    def get_python_value(self):
        raise NotImplementedError()
    def write(self, out: BinaryIO):
        raise NotImplementedError()

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
    def write(self, out: BinaryIO):
        out.write(self.value.to_bytes(self.type.bits // 8, "little"))

class IntegerValue(ScalarValue):
    def __init__(self, type: Integer, value):
        super().__init__(type, value)
        self.type: Integer
    def write(self, out: BinaryIO):
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

    def write(self, out: BinaryIO):
        for f in self.type.fields:
            self.values[f.name].write(out)
    
class TensorValue(Value):
    def __init__(self, type: Tensor, value):
        super().__init__(type)
        self.type: Tensor
        self.value = value

class VectorValue(Value):
    def __init__(self, type: Vector, value):
        super().__init__(type)
        self.type: Vector
        self.value = value
