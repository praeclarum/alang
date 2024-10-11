from alang import define, global_module, Module

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
