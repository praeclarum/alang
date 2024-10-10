from modules import Module
from funcs import Function
from lang import a_lang
from wgsl import wgsl_lang

global_module = Module("global")

def define(name: str, *parameters: list) -> Function:
    return global_module.define(name, *parameters)

if __name__ == "__main__":
    print()
    pass

