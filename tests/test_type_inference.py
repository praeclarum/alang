from alang import define, Compiler

def test_infer_void_return_type():
    f = define("f")
    assert f.return_type is None
    c = Compiler(f)
    did_infer = c.infer_types()
    assert did_infer
    assert f.return_type.name == "void"

def test_infer_const_return_type():
    f = define("f").ret(42)
    assert f.return_type is None
    c = Compiler(f)
    did_infer = c.infer_types()
    assert did_infer
    assert f.return_type.name == "int"
