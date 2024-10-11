from alang import struct

def test_struct():
    s = struct("Point", ("x", "int"), ("y", "int"))
    assert s.code.strip() == """
struct Point:
    x: int
    y: int
    """.strip()

def test_wgsl_struct():
    s = struct(
        "Point",
        ("x", "int"),
        ("y", "int"),
    )
    assert s.wgsl_code.strip() == """
struct Point {
    x: i32,
    y: i32
}""".strip()
