from nodes import Node

class Compiler:
    def __init__(self, ast: Node):
        self.ast = ast

    def infer_types(self) -> bool:
        """Performs one step of type inference on the AST.
        For full inference, keep running this method until it returns False.
        """
        return False
