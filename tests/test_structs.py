from alang import struct

def test_struct():
    s = struct("Point", ("x", "int"), ("y", "int"))
    assert s.code.strip() == """
struct Point:
    x: int
    y: int
    """.strip()

def test_struct_layout():
    s = struct(
        "Ray",
        ("id", "int"),
        ("position", "vec3f"),
        ("direction", "vec3f"),
    )
    l = s.layout
    fs = l.fields
    assert len(fs) == 3
    assert fs[0].offset == 0
    assert fs[0].align == 4
    assert fs[0].size == 4

def test_wgsl_struct():
    s = struct(
        "Ray",
        ("id", "int"),
        ("position", "vec3f"),
        ("direction", "vec3f"),
    )
    assert s.wgsl_code.strip() == """
struct Ray {
    id: i32,
    position: vec3<f32>,
    direction: vec3<f32>
}""".strip()
