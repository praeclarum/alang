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
        self.write_multiline_comment(f"ERROR! {message}")

    def warning(self, message: str):
        self.write_multiline_comment(f"WARNING: {message}")

    def write_error_value(self, message: str, type: Optional["typs.Type"] = None): # type: ignore
        self.write_zero_value_for_type(type)
        self.write_inline_comment(f"ERROR! {message}")

    def write_inline_comment(self, comment: str):
        raise NotImplementedError

    def write_line_comment(self, comment: str):
        raise NotImplementedError

    def write_diags(self, diags: list["DiagnosticMessage"]): # type: ignore
        for d in diags:
            m = d.message
            if d.node is not None:
                m += f" {d.node}"
            m = m.strip()
            if d.kind == "error":
                self.error(m)
            elif d.kind == "warning":
                self.warning(m)

    def write_alias(self, b: "Alias"): # type: ignore
        raise NotImplementedError

    def write_array(self, b: "Array"): # type: ignore
        raise NotImplementedError

    def write_binop(self, b: "Binop"): # type: ignore
        raise NotImplementedError

    def write_constant(self, c: "Constant"): # type: ignore
        raise NotImplementedError

    def write_expr(self, e: "Expression"): # type: ignore
        return self.write_node(e)

    def write_expr_stmt(self, e: "ExprStmt"): # type: ignore
        raise NotImplementedError

    def write_loop(self, f: "Loop"): # type: ignore
        raise NotImplementedError

    def write_funcall(self, f: "Funcall"): # type: ignore
        raise NotImplementedError

    def write_function(self, f):
        raise NotImplementedError

    def write_index(self, i: "Index"): # type: ignore
        raise NotImplementedError

    def write_module(self, m: "modules.Module"): # type: ignore
        for type in m.types:
            self.write_type(type)
        for func in m.functions:
            self.write_function(func)

    def write_multiline_comment(self, comment: str):
        lines = comment.split("\n")
        for line in lines:
            self.write_line_comment(line)

    def write_name(self, n: "Name"): # type: ignore
        raise NotImplementedError
    
    def write_node(self, n: "Node"): # type: ignore
        if n.node_type == nodes.NodeType.ALIAS:
            self.write_alias(n)
        elif n.node_type == nodes.NodeType.ARRAY:
            self.write_array(n)
        elif n.node_type == nodes.NodeType.BINOP:
            self.write_binop(n)
        elif n.node_type == nodes.NodeType.EXPR_STMT:
            self.write_expr_stmt(n)
        elif n.node_type == nodes.NodeType.CONSTANT:
            self.write_constant(n)
        elif n.node_type == nodes.NodeType.FUNCALL:
            self.write_funcall(n)
        elif n.node_type == nodes.NodeType.FUNCTION:
            self.write_function(n)
        elif n.node_type == nodes.NodeType.INDEX:
            self.write_index(n)
        elif n.node_type == nodes.NodeType.LOOP:
            self.write_loop(n)
        elif n.node_type == nodes.NodeType.MODULE:
            self.write_module(n)
        elif n.node_type == nodes.NodeType.NAME:
            self.write_name(n)
        elif n.node_type == nodes.NodeType.RETURN:
            self.write_return(n)
        elif n.node_type == nodes.NodeType.SET:
            self.write_set(n)
        elif n.node_type == nodes.NodeType.STRUCT:
            self.write_struct(n)
        else:
            raise ValueError(f"Cannot write node of type \"{n.node_type}\"")

    def write_return(self, r: "Return"): # type: ignore
        raise NotImplementedError

    def write_set(self, r: "Set"): # type: ignore
        raise NotImplementedError

    def write_stmt(self, s: "Statement"): # type: ignore
        return self.write_node(s)

    def write_struct(self, s):
        raise NotImplementedError

    def write_support_node(self, n: "Node"): # type: ignore
        return self.write_node(n)

    def write_type(self, t: "typs.Type"): # type: ignore
        if t.node_type == nodes.NodeType.STRUCT:
            self.write_struct(t)
        else:
            self.write(f"    // {t.name}\n")

    def write_zero_value_for_type(self, type: Optional["typs.Type"] = None): # type: ignore
        raise NotImplementedError
