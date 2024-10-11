from alang import struct

def test_struct():
    s = struct("Point", ("x", "int32"), ("y", "int32"))
    code = s.get_code()
    assert code == "struct Point {\n    int32 x;\n    int32 y;\n}\n"
