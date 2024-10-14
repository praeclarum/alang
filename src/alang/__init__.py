import typing

from funcs import Function
from nodes import AccessMode, AddressSpace, CodeOptions, Module, Variable

from typs import Array, Struct, Vector, Tensor, int_type, float_type, tensor_type

from langs import get_language

from compiler import Compiler

global_module = Module("global", can_define_statements=True)

def array(element_type: str, length: typing.Optional[int] = None) -> Array:
    return global_module.array(element_type, length)

def define(name: str, *parameters: list) -> Function:
    return global_module.define(name, *parameters)

def loop(var: str, count, body = None) -> Array:
    return global_module.loop(var, count, body)

def struct(name: str, *fields: list) -> Struct:
    return global_module.struct(name, *fields)

if __name__ == "__main__":
    pass
