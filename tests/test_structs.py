from alang import struct

def test_struct():
    s = struct("Point", ("x", "int32"), ("y", "int32"))
    code = s.get_code()
    assert code.strip() == """
struct Point:
    x: int32
    y: int32
    """.strip()
