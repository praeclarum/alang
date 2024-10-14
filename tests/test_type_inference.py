from alang import define, Compiler, CodeOptions

def test_infer_void_return_type():
    f = define("f")
    assert f.return_type is None
    c = Compiler(f, CodeOptions())
    c.compile()
    assert f.return_type.name == "void"

def test_infer_const_return_type():
    f = define("f").ret(42)
    assert f.return_type is None
    c = Compiler(f, CodeOptions())
    c.compile()
    assert f.return_type.name == "int"
