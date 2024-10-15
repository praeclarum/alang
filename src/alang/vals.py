from alang.typs import Array, Scalar, Struct, Tensor, Vector

class Value:
    def __init__(self):
        pass

class ScalarValue(Value):
    def __init__(self, type: Scalar, value):
        super().__init__()
        self.type: Scalar = type
        self.value = value

class StructValue(Value):
    def __init__(self, type: Struct, **kwargs):
        super().__init__()
        self.type: Struct = type

    def find_field(self, name: str):
        for f in self.type.fields:
            if f.name == name:
                return f
        return None

    def __getattr__(self, name: str):
        f = self.find_field(name)
        return None
    
class TensorValue(Value):
    def __init__(self, type: Tensor, value):
        super().__init__()
        self.type: Tensor = type
        self.value = value

class VectorValue(Value):
    def __init__(self, type: Vector, value):
        super().__init__()
        self.type: Vector = type
        self.value = value
