from typing import Optional, TextIO, Union

import nodes

class CodeWriter:
    def __init__(self, path_or_io: Union[str, TextIO], options: Optional["CodeOptions"]): # type: ignore
        self.options = options
        if self.options is None:
            from nodes import CodeOptions
            self.options = CodeOptions()
        if type(path_or_io) is str:
            self.out = open(path_or_io, "w")
            self.owner = True
        else:
            self.out = path_or_io
            self.owner = False
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
    def write(self, s: str):
        self.out.write(s)
    def close(self):
        if self.owner and self.out is not None:
            self.out.close()
            self.out = None
            self.owner = False

    def error(self, message: str):
        print(f"WARNING: {message}")

    def warning(self, message: str):
        print(f"WARNING: {message}")

    def write_node(self, n: "Node"): # type: ignore
        if n.node_type == nodes.NodeType.MODULE:
            self.write_module(n)
        elif n.node_type == nodes.NodeType.FUNCTION:
            self.write_function(n)
        elif n.node_type == nodes.NodeType.STRUCT:
            self.write_struct(n)
        else:
            raise ValueError(f"Cannot write node of type {n.node_type}")

    def write_module(self, m: "modules.Module"): # type: ignore
        for type in m.types:
            self.write_type(type)
        for func in m.functions:
            self.write_function(func)

    def write_type(self, t: "typs.Type"): # type: ignore
        if t.node_type == nodes.NodeType.STRUCT:
            self.write_struct(t)
        else:
            self.write(f"    // {t.name}\n")

    def write_struct(self, s):
        raise NotImplementedError

    def write_function(self, f):
        raise NotImplementedError

    def write_statement(self, s: "Statement"): # type: ignore
        if s.node_type == nodes.NodeType.RETURN:
            self.write_return(s)
        else:
            raise ValueError(f"Cannot write statement of type {s.node_type}")
        
    def write_return(self, r: "Return"): # type: ignore
        raise NotImplementedError
        
    def write_expr(self, e: "Expression"): # type: ignore
        if e.node_type == nodes.NodeType.NAME:
            self.write_name(e)
        elif e.node_type == nodes.NodeType.BINOP:
            self.write_binop(e)
        else:
            raise ValueError(f"Cannot write expression of type {e.node_type}")
    
    def write_name(self, n: "Name"): # type: ignore
        raise NotImplementedError
    
    def write_binop(self, b: "Binop"): # type: ignore
        raise NotImplementedError
