from nodes import Expression, NodeAttr

class Name(Expression):
    name = NodeAttr()
    def __init__(self, name: str):
        super().__init__()
        self.name = name
    def __str__(self):
        return self.name
    def __repr__(self):
        return f"Name({self.name})"
