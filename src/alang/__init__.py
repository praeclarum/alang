from modules import Module
from alang.funcs import Function

global_module = Module("global")

def define(name: str, *parameters: list) -> Function:
    return global_module.define(name, *parameters)

if __name__ == "__main__":
    print()
    pass

