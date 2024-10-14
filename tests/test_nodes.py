from alang import define, global_module, float_type, Module, AccessMode, AddressSpace, Function, Variable

def test_define():
    f_count = len(global_module.functions)
    n = define("f", "x")
    assert n.name == "f"
    assert len(n.parameters) == 1
    assert n.parameters[0].name == "x"
    assert len(global_module.functions) == f_count + 1

def test_has_global_module():
    assert global_module is not None
    assert global_module.name == "global"

def test_new_module():
    m = Module("test")
    m.define("f", "x")
    m.define("g", "y")
    assert m.name == "test"
    assert len(m.functions) == 2
    assert m.functions[0].name == "f"
    assert m.functions[1].name == "g"

def test_var():
    f = define("f", "x").set("y", "2*x").ret("y")
    assert len(f.variables) == 1

def test_module_var_default_address_space():
    m = Module("test")
    m.var("x", "int")
    v = m.variables[0]
    assert v.address_space == AddressSpace.PRIVATE
    assert v.access_mode == "read_write"
    assert m.wgsl_code.strip() == """
var<private> x: i32;
""".strip()

def test_module_var_default_storage_access_mode():
    m = Module("test")
    m.var("x", "int", address_space=AddressSpace.STORAGE)
    v = m.variables[0]
    assert v.address_space == AddressSpace.STORAGE
    assert v.access_mode == "read"
    assert m.wgsl_code.strip() == """
var<storage, read> x: i32;
""".strip()

def test_module_var_storage_read_write_access_mode():
    m = Module("test")
    m.var("x", "int", address_space=AddressSpace.STORAGE, access_mode=AccessMode.READ_WRITE)
    v = m.variables[0]
    assert v.address_space == AddressSpace.STORAGE
    assert v.access_mode == "read_write"
    assert m.wgsl_code.strip() == """
var<storage, read_write> x: i32;
""".strip()

def test_function_var_default_address_space():
    m = Module("test")
    m.define("f").var("x", "int")
    f: Function = m.functions[0]
    v: Variable = f.variables[0]
    assert v.address_space is not None
    assert v.access_mode == "read_write"
    assert v.address_space == "function"
    assert f.wgsl_code.strip() == """
fn f() {
    var x: i32;
}
""".strip()

def test_pointer_param():
    f = define("f").param("x", float_type.ptr(address_space=AddressSpace.STORAGE))
    assert f.parameters[0].parameter_type.name == "float*"
    assert f.wgsl_code.strip() == """
fn f(x: ptr<storage, f32>) {
}
""".strip()
    assert f.c_code.strip() == """
void f(float* x) {
}
""".strip()
