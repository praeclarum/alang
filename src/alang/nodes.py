import io
from typing import Any, Callable, Optional, TextIO, TypeVar, Union

import langs

TypeRef = str

Code = str
class CodeOptions:
    def __init__(self, standalone: bool = False, struct_annotations: bool = False, auto_entry_points: bool = False) -> None:
        self.standalone = standalone
        self.struct_annotations = struct_annotations
        self.auto_entry_points = auto_entry_points
        self.entry_points = []

class NodeType:
    ADDRESS = 'address'
    ALIAS = 'alias'
    ARRAY = 'array'
    BINOP = 'binop'
    CONSTANT = 'constant'
    EXPR_STMT = 'expr_stmt'
    FIELD = 'field'
    FLOAT = 'float'
    FUNCALL = 'funcall'
    FUNCTION = 'function'
    FUNCTION_TYPE = 'function_type'
    INDEX = 'index'
    INTEGER = 'integer'
    LOOP = 'loop'
    MEMBER = 'member'
    MODULE = 'module'
    MODULE_TYPE = 'module_type'
    NAME = 'name'
    PARAMETER = 'parameter'
    POINTER = 'pointer'
    RETURN = 'return'
    SET = 'set'
    STRUCT = 'struct'
    SWIZZLE = 'swizzle'
    TENSOR = 'tensor'
    TYPE_NAME = 'type_name'
    VARIABLE = 'variable'
    VOID = 'void'
    VECTOR = 'vector'

next_node_id = 1

class Node:
    def __init__(self, type: str):
        global next_node_id
        self.id = next_node_id
        next_node_id += 1
        self.node_type = type
        self.attributes: dict[str, "NodeAttr"] = {}
        self.links: list[tuple[str, "Node"]] = []
        self.last_backlink: Optional["Node"] = None
        self.resolved_type = None # all nodes get typed
        self.resolved_node = None # some nodes (name, type_name) get resolved to a node
    def append_backlink(self, backlink: "Node", rel: str):
        self.last_backlink = backlink
    def get_rels(self, rel: str) -> list["Node"]:
        return [child for (crel, child) in self.links if crel == rel]
    def get_rel(self, rel: str) -> Optional["Node"]:
        cs = self.get_rels(rel)
        return cs[0] if len(cs) > 0 else None
    def link(self, child: "Node", rel: str) -> "Node":
        if child is None:
            raise ValueError(f"Cannot link {repr(self.node_type)} node to None (rel={rel})")
        if not isinstance(child, Node):
            raise ValueError(f"Cannot link {repr(self.node_type)} node to {repr(child)} (rel={rel})")
        self.links.append((rel, child))
        child.append_backlink(self, rel)
        return self
    def find_reachable_with_type(self, node_type: NodeType) -> list["Node"]:
        reachable = []
        if self.node_type == node_type:
            reachable.append(self)
        for rel, link in self.links:
            reachable.extend(link.find_reachable_with_type(node_type))
        return reachable
    def write_node(self, out, depth, rel):
        if depth > 5:
            out.write("...")
            return
        indent = "    " * depth
        out.write(f"{indent}({self.node_type} (")
        head = ""
        for k, a in self.attributes.items():
            out.write(f"{head}{a.name}={repr(getattr(self, a.private_name))}")
            head = " "
        if len(self.links) > 0:
            out.write(")\n")
            for crel, child in self.links:
                child.write_node(out, depth + 1, crel)
            out.write(f"{indent})\n")
        else:
            out.write("))\n")
    def __str__(self):
        out = io.StringIO()
        self.write_node(out, 0, None)
        return out.getvalue()
    def __repr__(self):
        return str(self)
    def lookup_variable(self, name: str) -> Optional["Variable"]:
        p = self.last_backlink
        while p is not None:
            if isinstance(p, Node):
                return p.lookup_variable(name)
            p = p.parent
        return None
    def resolve_type(self, diags) -> Optional["Type"]: # type: ignore
        raise NotImplementedError(f"resolve_type not implemented for {self.node_type}")
    def get_support_definitions(self, defs: "compiler.SupportDefinitions"): # type: ignore
        pass
    def write_code(self, out: Union[str, TextIO], language: Optional[Any] = None, options: Optional[CodeOptions] = None):
        from compiler import Compiler
        options = options or CodeOptions()
        language = langs.get_language(language)
        compiler = Compiler(self, options)
        compiler.compile()
        options.entry_points = compiler.entry_points
        with language.open_writer(out, options) as writer:
            for s in compiler.support_definitions:
                writer.write_support_node(s)
            writer.write_node(self)
            writer.write_diags(compiler.diags.messages)
    def get_code(self, language: Optional[Any] = None, options: Optional[CodeOptions] = None) -> str:
        out = io.StringIO()
        self.write_code(out, language, options)
        code = out.getvalue()
        return code
    @property
    def code(self) -> str:
        return self.get_code("a")
    @property
    def c_code(self) -> str:
        return self.get_code("c")
    @property
    def html_code(self) -> str:
        return self.get_code("html")
    @property
    def js_code(self) -> str:
        return self.get_code("js")
    @property
    def wgsl_code(self) -> str:
        return self.get_code("wgsl")
    
class NodeAttr:
    def __init__(self, default_value=None):
        self.default_value = default_value
    def __set_name__(self, owner: Node, name: str):
        self.name = name
        self.private_name = f"_{name}"
    def __get__(self, obj: Node, objtype=None):
        if hasattr(obj, self.private_name):
            return getattr(obj, self.private_name)
        return self.default_value
    def __set__(self, obj: Node, value):
        obj.attributes[self.name] = self
        setattr(obj, self.private_name, value)

class NodeLinks:
    def __init__(self):
        self.rel = None
    def __set_name__(self, owner: Node, name: str):
        self.rel = name
    def __get__(self, obj: Node, objtype=None) -> list[Node]:
        return obj.get_rels(self.rel)
    def __set__(self, obj: Node, value: list[Node]):
        i = 0
        while i < len(obj.links):
            if obj.links[i][0] == self.rel:
                ch = obj.links.pop(i)[1]
                ch.last_backlink = None
            else:
                i += 1
        for child in value:
            obj.link(child, self.rel)

class NodeLink:
    def __init__(self):
        self.rel = None
    def __set_name__(self, owner: Node, name: str):
        self.rel = name
    def __get__(self, obj: Node, objtype=None) -> list[Node]:
        return obj.get_rel(self.rel)
    def __set__(self, obj: Node, value: Optional[Node]):
        i = 0
        while i < len(obj.links):
            if obj.links[i][0] == self.rel:
                ch = obj.links.pop(i)[1]
                ch.last_backlink = None
            else:
                i += 1
        if value is not None:
            obj.link(value, self.rel)

class Visitor:
    def visit(self, node: Node, parent: Node, rel: str, acc):
        raise NotImplementedError()
    def visit_node(self, node: Node, parent: Node, rel: str, acc):
        if node.node_type == NodeType.ALIAS:
            return self.visit_alias(node, parent, rel, acc)
        elif node.node_type == NodeType.ARRAY:
            return self.visit_array(node, parent, rel, acc)
        elif node.node_type == NodeType.BINOP:
            return self.visit_binop(node, parent, rel, acc)
        elif node.node_type == NodeType.CONSTANT:
            return self.visit_constant(node, parent, rel, acc)
        elif node.node_type == NodeType.EXPR_STMT:
            return self.visit_expr_stmt(node, parent, rel, acc)
        elif node.node_type == NodeType.FIELD:
            return self.visit_field(node, parent, rel, acc)
        elif node.node_type == NodeType.FLOAT:
            return self.visit_float(node, parent, rel, acc)
        elif node.node_type == NodeType.FUNCALL:
            return self.visit_funcall(node, parent, rel, acc)
        elif node.node_type == NodeType.FUNCTION:
            return self.visit_function(node, parent, rel, acc)
        elif node.node_type == NodeType.INDEX:
            return self.visit_index(node, parent, rel, acc)
        elif node.node_type == NodeType.INTEGER:
            return self.visit_integer(node, parent, rel, acc)
        elif node.node_type == NodeType.LOOP:
            return self.visit_loop(node, parent, rel, acc)
        elif node.node_type == NodeType.MEMBER:
            return self.visit_member(node, parent, rel, acc)
        elif node.node_type == NodeType.MODULE:
            return self.visit_module(node, parent, rel, acc)
        elif node.node_type == NodeType.NAME:
            return self.visit_name(node, parent, rel, acc)
        elif node.node_type == NodeType.PARAMETER:
            return self.visit_parameter(node, parent, rel, acc)
        elif node.node_type == NodeType.POINTER:
            return self.visit_pointer(node, parent, rel, acc)
        elif node.node_type == NodeType.RETURN:
            return self.visit_return(node, parent, rel, acc)
        elif node.node_type == NodeType.SET:
            return self.visit_set(node, parent, rel, acc)
        elif node.node_type == NodeType.STRUCT:
            return self.visit_struct(node, parent, rel, acc)
        elif node.node_type == NodeType.SWIZZLE:
            return self.visit_swizzle(node, parent, rel, acc)
        elif node.node_type == NodeType.TENSOR:
            return self.visit_tensor(node, parent, rel, acc)
        elif node.node_type == NodeType.VARIABLE:
            return self.visit_variable(node, parent, rel, acc)
        elif node.node_type == NodeType.VECTOR:
            return self.visit_vector(node, parent, rel, acc)
        elif node.node_type == NodeType.VOID:
            return self.visit_void(node, parent, rel, acc)
        else:
            missing_code = f"elif node.node_type == NodeType.{node.node_type.upper()}:\n    return self.visit_{node.node_type.lower()}(node, parent, rel, acc)"
            print(missing_code)
            return acc
    def visit_address(self, node: "Address", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_alias(self, node: "Alias", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_array(self, node: "Array", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_binop(self, node: "Binop", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_constant(self, node: "Constant", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_expr_stmt(self, node: "ExprStmt", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_field(self, node: "Field", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_float(self, node: "Float", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_loop(self, node: "Loop", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_funcall(self, node: "Funcall", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_function(self, node: "Function", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_index(self, node: "Index", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_integer(self, node: "Integer", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_member(self, node: "Member", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_module(self, node: "Module", parent: Node, rel: str, acc):
        return acc
    def visit_name(self, node: "Name", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_parameter(self, node: "Parameter", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_pointer(self, node: "Pointer", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_return(self, node: "Return", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_set(self, node: "Set", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_swizzle(self, node: "Swizzle", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_struct(self, node: "Struct", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_tensor(self, node: "Tensor", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_variable(self, node: "Variable", parent: Node, rel: str, acc):
        return acc
    def visit_vector(self, node: "Vector", parent: Node, rel: str, acc): # type: ignore
        return acc
    def visit_void(self, node: "Void", parent: Node, rel: str, acc): # type: ignore
        return acc
    
class DepthFirstVisitor(Visitor):
    def visit(self, node: Node, parent: Node, rel: str, acc):
        sacc = []
        for crel, child in node.links:
            sacc.append((crel, self.visit(child, node, crel, acc)))
        return self.visit_node(node, parent, rel, sacc)

class BreadthFirstVisitor(Visitor):
    def visit(self, node: Node, parent: Node, rel: str, acc):
        cacc = self.visit_node(node, parent, rel, acc)
        for crel, child in node.links:
            self.visit(child, node, crel, cacc)

class Expression(Node):
    def __init__(self, node_type: NodeType):
        super().__init__(node_type)
    def __add__(self, other: "Expression") -> "Expression":
        return self.add(other)
    def add(self, other: "Expression") -> "Expression":
        from exprs import Binop
        return Binop(self, "+", other)
    def __sub__(self, other: "Expression") -> "Expression":
        return self.sub(other)
    def sub(self, other: "Expression") -> "Expression":
        from exprs import Binop
        return Binop(self, "-", other)
    def __mul__(self, other: "Expression") -> "Expression":
        return self.mul(other)
    def mul(self, other: "Expression") -> "Expression":
        from exprs import Binop
        return Binop(self, "*", other)
    def __truediv__(self, other: "Expression") -> "Expression":
        return self.div(other)
    def div(self, other: "Expression") -> "Expression":
        from exprs import Binop
        return Binop(self, "/", other)

class Statement(Node):
    def __init__(self, node_type: NodeType):
        super().__init__(node_type)

class Block(Node):
    types = NodeLinks()
    variables = NodeLinks()
    functions: list["funcs.Functions"] = NodeLinks() # type: ignore
    statements = NodeLinks()
    def __init__(self, type: NodeType, can_define_types: bool, can_define_functions: bool, can_define_variables: bool, can_define_statements: bool):
        super().__init__(type)
        self.can_define_types = can_define_types
        self.can_define_functions = can_define_functions
        self.can_define_variables = can_define_variables
        self.can_define_statements = can_define_statements
    def parse_type(self, expr: Optional[Code]) -> Optional["Type"]: # type: ignore
        from typs import try_resolve_type
        return try_resolve_type(expr, self)
    def parse_expr(self, expr: Optional[Code]) -> Optional["Expression"]:
        from exprs import parse_expr
        return parse_expr(expr, self)
    def parse_stmt(self, stmt: Optional[Code]) -> Optional["Expression"]:
        return self.parse_expr(stmt)
    def append_any(self, child: Node):
        if child.node_type == NodeType.ARRAY:
            self.link(child, "types")
        elif child.node_type == NodeType.STRUCT:
            self.link(child, "types")
        elif child.node_type == NodeType.VARIABLE:
            self.link(child, "variables")
        elif child.node_type == NodeType.FUNCTION:
            self.link(child, "functions")
        elif isinstance(child, Statement):
            self.link(child, "statements")
        else:            
            raise ValueError(f"Cannot append {child.node_type} to {self.node_type}")
    def array(self, element_type: str, length: Optional[int] = None) -> "Array": # type: ignore
        if self.can_define_types:
            from typs import Array
            a = Array(element_type, length)
            self.link(a, "types")
            return a
        else:
            raise ValueError(f"Cannot define array in {self.node_type}")
    def call(self, func: str, *args: list) -> "Block":
        from exprs import Funcall
        from stmts import ExprStmt
        func = self.parse_expr(func)
        args = [self.parse_expr(x) for x in args]
        funcall = Funcall(func, args)
        call_stmt = ExprStmt(funcall)
        self.stmt(call_stmt)
        return self
    def define(self, name: str, *parameters: list) -> "Function": # type: ignore
        if self.can_define_functions:
            from funcs import Function
            f = Function(name, None, *parameters)
            self.link(f, "functions")
            return f
        else:
            raise ValueError(f"Cannot define function in {self.node_type}")
    def loop(self, var: str, count: Code, *statements: list[Code]) -> "Block": # type: ignore
        from stmts import Loop
        count = self.parse_expr(count)
        loop = Loop(var, count, *statements)
        self.stmt(loop)
        return self
    def ret(self, value: Optional[Code]) -> "Block":
        from stmts import Return
        r = Return(self.parse_expr(value))
        self.stmt(r)
        return self
    def set(self, lhs: Code, rhs: Code) -> "Block":
        lhs = self.parse_expr(lhs)
        rhs = self.parse_expr(rhs)
        v = self.lookup_variable(lhs)
        if v is None:
            if self.can_define_variables:
                v = Variable(lhs)
                self.link(v, "variables")
            else:
                raise ValueError(f"Variable {lhs} not defined")
        else:
            raise ValueError(f"Variable {lhs} already defined")
        return self
    def stmt(self, stmt):
        if not self.can_define_statements:
            raise ValueError(f"Cannot define return statements in {self.node_type}")
        self.link(stmt, "statements")
    def struct(self, name: str, *fields: list) -> "Struct": # type: ignore
        if self.can_define_types:
            from typs import Struct
            s = Struct(name)
            for field in fields:
                s.field(*field)
            self.link(s, "types")
            return s
        else:
            raise ValueError(f"Cannot define struct in {self.node_type}")
    def get_default_address_space(self) -> Optional[str]:
        return None
    def var(
            self,
            name: str, type: Optional["Type"] = None, initial_value: Expression = None, # type: ignore
            bind_group: Optional[int] = None, binding: Optional[int] = None,
            address_space: Optional[str] = None, access_mode: Optional[str] = None,
            ) -> "Block":
        if self.can_define_variables:
            type = self.parse_type(type)
            if address_space is None:
                address_space = self.get_default_address_space()
            v = Variable(name,
                         type=type, initial_value=initial_value,
                         bind_group=bind_group, binding=binding,
                         address_space=address_space, access_mode=access_mode)
            self.link(v, "variables")
            return self
        else:
            raise ValueError(f"Variable {name} not defined")
        
class AddressSpace:
    FUNCTION = 'function'
    PRIVATE = 'private'
    STORAGE = 'storage'
    UNIFORM = 'uniform'
    WORKGROUP = 'workgroup'

class AccessMode:
    READ = 'read'
    WRITE = 'write'
    READ_WRITE = 'read_write'

class Module(Block):
    name = NodeAttr()

    def __init__(self, name: str, can_define_statements: bool = False):
        super().__init__(NodeType.MODULE, can_define_types=True, can_define_functions=True, can_define_variables=True, can_define_statements=can_define_statements)
        if name is not None:
            self.name = name

    def get_default_address_space(self) -> Optional[str]:
        return AddressSpace.PRIVATE

    def resolve_type(self, diags: "compiler.Diagnostics") -> "typs.Type": # type: ignore
        from typs import ModuleType
        return ModuleType(self.name)

def get_default_access_mode_for_address_space(address_space: str) -> str:
    if address_space == AddressSpace.FUNCTION:
        return AccessMode.READ_WRITE
    elif address_space == AddressSpace.PRIVATE:
        return AccessMode.READ_WRITE
    elif address_space == AddressSpace.WORKGROUP:
        return AccessMode.READ_WRITE
    elif address_space == AddressSpace.UNIFORM:
        return AccessMode.READ
    elif address_space == AddressSpace.STORAGE:
        return AccessMode.READ
    else:
        raise ValueError(f"Invalid address space: {address_space}")

class Variable(Node):
    # https://www.w3.org/TR/WGSL/#var-decls
    name = NodeAttr()
    variable_type = NodeLink()
    initial_value = NodeLink()
    address_space = NodeAttr()
    access_mode = NodeAttr()

    def __init__(
            self,
            name: str, type: Optional["Type"] = None, initial_value: Expression = None, # type: ignore
            bind_group: Optional[int] = None, binding: Optional[int] = None,
            address_space: Optional[str] = None, access_mode: Optional[str] = None,
            ):
        super().__init__(NodeType.VARIABLE)
        self.name = name
        self.variable_type = type
        self.initial_value = initial_value
        self.bind_group = bind_group
        self.binding = binding
        self.address_space = address_space
        self.access_mode = access_mode
        # The address space must be specified if the access mode is specified.
        if self.access_mode is not None and self.address_space is None:
            raise ValueError(f"The address space must be specified if the access mode is specified")
        # The access mode always has a default value, and except for variables in the storage address space, must not be specified in the WGSL source.
        if self.access_mode is not None and self.address_space != AddressSpace.STORAGE:
            raise ValueError(f"Cannot specify access mode for {repr(self.address_space)} address space")
        if self.address_space is not None and self.access_mode is None:
            self.access_mode = get_default_access_mode_for_address_space(self.address_space)
    
    def resolve_type(self, diags: "compiler.Diagnostics") -> "typs.Type": # type: ignore
        if self.variable_type is None:
            return None
        return self.variable_type.resolved_type
