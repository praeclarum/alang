from alang import *

def test_define():
    n = define("f", "x")
    assert n.name == "f"
    assert len(n.parameters) == 1
    assert n.parameters[0].name == "x"
