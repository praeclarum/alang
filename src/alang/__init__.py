from nodes import NodeType, TypeRef, Function

def define(name: str, *parameters: list[tuple[str, TypeRef]]) -> Function:
    n = Function(name)
    for param in parameters:
        n.parameter(param)
    return n

if __name__ == "__main__":
    print(define("f", "x"))
    pass

