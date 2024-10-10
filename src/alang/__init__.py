from nodes import Module, NodeType, TypeRef, Function

global_module = Module("global")

def define(name: str, *parameters: list[tuple[str, TypeRef]]) -> Function:
    return global_module.define(name, *parameters)

if __name__ == "__main__":
    print()
    pass

