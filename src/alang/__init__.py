from typing import Optional
from modules import Module
from funcs import Function
from nodes import Node, NodeType, CodeOptions

from typs import Array, Struct, Vector, Tensor, int_type, float_type, tensor_type

from langs import get_language

from compiler import Compiler

global_module = Module("global")

def define(name: str, *parameters: list) -> Function:
    return global_module.define(name, *parameters)

def struct(name: str, *fields: list) -> Struct:
    return global_module.struct(name, *fields)

def array(element_type: str, length: Optional[int] = None) -> Array:
    return global_module.array(element_type, length)

if __name__ == "__main__":
    print()
    pass

