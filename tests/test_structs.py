from alang import struct

def test_struct():
    s = struct("Point", ("x", "int32"), ("y", "int32"))
    assert s.code.strip() == """
struct Point:
    x: int32
    y: int32
    """.strip()

def test_wgsl_struct():
    s = struct(
        "Point",
        ("x", "int32"),
        ("y", "int32"),
    )
    assert s.wgsl_code.strip() == """
struct Point {
    x: int32,
    y: int32
}""".strip()
