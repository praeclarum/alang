from modules import Module
from funcs import Function
from typs import Struct

global_module = Module("global")

def define(name: str, *parameters: list) -> Function:
    return global_module.define(name, *parameters)

def struct(name: str, *fields: list) -> Struct:
    return global_module.struct(name, *fields)

if __name__ == "__main__":
    print()
    pass

